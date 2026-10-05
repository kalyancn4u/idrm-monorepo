/**
 * js/main.js — entry script for the PUBLIC landing page (index.html).
 *
 * The landing makes no API calls — it must load even if the backend is down
 * (critical during a disaster). Its only behavior: if the visitor is already
 * signed in, send them straight to their dashboard.
 */
import { redirectIfAuthed } from "./auth-guard.js";

redirectIfAuthed();
