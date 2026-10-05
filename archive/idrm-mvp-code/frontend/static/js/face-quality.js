/*
 * face-quality.js — client-side photo-quality gate for IDRM uploads (ADR-011).
 *
 * WHAT THIS IS (for a complete novice):
 *   Before a citizen uploads an incident photo or completion proof, this runs *in their own browser*
 *   and gives a friendly warning if the picture is likely poor — too small, too dark, blurry, or
 *   (optionally) with no clear face. It helps people take a usable photo the first time.
 *
 * WHY IT IS CLIENT-SIDE (privacy — DPDP Act 2023):
 *   The check runs ENTIRELY on the device. No image, no face data, and nothing biometric ever leaves
 *   the browser here, and nothing is stored. For faces we read ONLY the *count* ("is there ≥1 face?")
 *   and immediately discard everything else — we never keep or send face landmarks or identity. This
 *   is *detection-only*: telling a face is present, never *recognising whose* face it is. Identity
 *   matching (FaceNet) is out of the MVP and deferred to the FFP (ADR-011).
 *
 * IT IS ADVISORY, NOT A BLOCKER:
 *   This gate only *warns*. The authoritative checks (size ≤ 10 MB, min dimensions, EXIF/GPS stripped,
 *   blur, re-encode) run again on the SERVER in app/modules/files/imaging.py — because we never trust
 *   the client. If this module is unavailable or the browser lacks a feature, the upload still works.
 *
 * USAGE:
 *   <script src="/static/js/face-quality.js" defer></script>
 *   IDRMFaceQuality.attachTo(document.querySelector('#photo'), (result) => {
 *     // show result.warnings to the user (each has {code, message}); never hard-block on them
 *   }, { requireFace: false });
 */
(function (global) {
  "use strict";

  // Defaults mirror the server's media rules (app/core/config.py) so guidance matches enforcement.
  const DEFAULTS = Object.freeze({
    minWidth: 640,
    minHeight: 480,
    maxBytes: 10 * 1024 * 1024, // 10 MB
    minBrightness: 40, // 0–255 average luminance; below ≈ too dark
    maxBrightness: 225, // above ≈ washed out / overexposed
    minSharpness: 8, // adjacency-variance proxy; below ≈ likely blurry
    requireFace: false, // scene photos don't need a face; set true where a person is expected
    sampleMax: 256, // downscale longest edge to this for cheap pixel analysis
  });

  /** Decode a File/Blob into an ImageBitmap (fast, off-main-thread when supported). */
  async function decode(file) {
    if (global.createImageBitmap) {
      return await global.createImageBitmap(file);
    }
    // Fallback for older browsers: decode via an <img> and an object URL.
    return await new Promise((resolve, reject) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        URL.revokeObjectURL(url);
        resolve(img);
      };
      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error("decode_failed"));
      };
      img.src = url;
    });
  }

  /** Draw a downscaled grayscale copy and return {brightness, sharpness} from its pixels. */
  function analyzePixels(bitmap, sampleMax) {
    const w = bitmap.width || bitmap.naturalWidth;
    const h = bitmap.height || bitmap.naturalHeight;
    const scale = Math.min(1, sampleMax / Math.max(w, h));
    const sw = Math.max(1, Math.round(w * scale));
    const sh = Math.max(1, Math.round(h * scale));

    const canvas = global.OffscreenCanvas
      ? new global.OffscreenCanvas(sw, sh)
      : Object.assign(document.createElement("canvas"), { width: sw, height: sh });
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    ctx.drawImage(bitmap, 0, 0, sw, sh);
    const { data } = ctx.getImageData(0, 0, sw, sh);

    // Convert to a grayscale luminance array.
    const gray = new Float32Array(sw * sh);
    let sum = 0;
    for (let i = 0, p = 0; i < data.length; i += 4, p += 1) {
      const lum = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
      gray[p] = lum;
      sum += lum;
    }
    const brightness = sum / gray.length;

    // Sharpness proxy: variance of horizontal neighbour differences (blurry → low variance).
    let dSum = 0;
    let dSqSum = 0;
    let n = 0;
    for (let y = 0; y < sh; y += 1) {
      for (let x = 1; x < sw; x += 1) {
        const d = gray[y * sw + x] - gray[y * sw + x - 1];
        dSum += d;
        dSqSum += d * d;
        n += 1;
      }
    }
    const mean = n ? dSum / n : 0;
    const sharpness = n ? dSqSum / n - mean * mean : 0;
    return { brightness, sharpness };
  }

  /**
   * Best-effort face COUNT via the browser's on-device FaceDetector.
   * Returns a number, or null if the API is unavailable. We read only the count and discard the rest.
   */
  async function countFaces(bitmap) {
    if (typeof global.FaceDetector !== "function") {
      return null; // unsupported → skip the face check entirely (graceful degradation)
    }
    try {
      const detector = new global.FaceDetector({ fastMode: true, maxDetectedFaces: 5 });
      const faces = await detector.detect(bitmap);
      return Array.isArray(faces) ? faces.length : null; // count only; nothing stored/sent
    } catch (_err) {
      return null; // any failure → treat as "unknown", never block
    }
  }

  /**
   * Analyse a photo File and return quality guidance.
   * @returns {Promise<{ok:boolean, warnings:{code:string,message:string}[], info:object}>}
   */
  async function analyzePhoto(file, options) {
    const opts = Object.assign({}, DEFAULTS, options || {});
    const warnings = [];

    if (file && file.size > opts.maxBytes) {
      warnings.push({ code: "file_too_large", message: "This file is over 10 MB. Please compress it." });
    }

    let bitmap;
    try {
      bitmap = await decode(file);
    } catch (_err) {
      // Can't read it here — let the server be the judge; don't block.
      return { ok: true, warnings, info: { decoded: false } };
    }

    const width = bitmap.width || bitmap.naturalWidth;
    const height = bitmap.height || bitmap.naturalHeight;
    if (width < opts.minWidth || height < opts.minHeight) {
      warnings.push({
        code: "image_too_small",
        message: `Photo should be at least ${opts.minWidth}x${opts.minHeight}px.`,
      });
    }

    const { brightness, sharpness } = analyzePixels(bitmap, opts.sampleMax);
    if (brightness < opts.minBrightness) {
      warnings.push({ code: "image_too_dark", message: "Photo looks too dark — try more light." });
    } else if (brightness > opts.maxBrightness) {
      warnings.push({ code: "image_overexposed", message: "Photo looks washed out — reduce glare." });
    }
    if (sharpness < opts.minSharpness) {
      warnings.push({ code: "image_too_blurry", message: "Photo looks blurry — hold steady and retake." });
    }

    const faces = await countFaces(bitmap);
    if (opts.requireFace && faces === 0) {
      warnings.push({ code: "no_face_detected", message: "No clear face detected — please include the person." });
    }

    // Release the decoded image promptly (and, with it, all pixel data).
    if (bitmap.close) {
      bitmap.close();
    }

    return {
      ok: warnings.length === 0,
      warnings,
      info: { decoded: true, width, height, brightness: Math.round(brightness), sharpness: Math.round(sharpness), faces },
    };
  }

  /**
   * Wire the gate to a file <input>. On each selection, analyse the first file and call onResult.
   * Never prevents the upload — onResult decides how to surface warnings.
   */
  function attachTo(inputEl, onResult, options) {
    if (!inputEl) {
      return;
    }
    inputEl.addEventListener("change", async () => {
      const file = inputEl.files && inputEl.files[0];
      if (!file) {
        return;
      }
      try {
        const result = await analyzePhoto(file, options);
        if (typeof onResult === "function") {
          onResult(result);
        }
      } catch (_err) {
        // Analysis is best-effort; a failure must never break the upload flow.
        if (typeof onResult === "function") {
          onResult({ ok: true, warnings: [], info: { error: true } });
        }
      }
    });
  }

  global.IDRMFaceQuality = { analyzePhoto, attachTo, DEFAULTS };
})(window);
