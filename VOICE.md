# Voice routes and limits

Voice reuses the browser/device capabilities or separately configured online providers. NexusAI does not bundle a speech-recognition model or a premium speech-synthesis voice, and this release does not establish recognition accuracy, acoustic quality, or realistic real-world interruption handling.

| Route | Behavior | Boundary |
| --- | --- | --- |
| Strict-offline dictation | Requires an available browser on-device recognition API and installed language pack; requests `processLocally` | Fails clearly when unavailable; no cloud-recognition fallback or automatic language-pack download |
| Browser recognition with offline lock disabled | Uses the browser/OS recognition implementation | May transmit audio to its speech service; browser behavior determines availability and microphone choice |
| Configured API recorder | Records through the explicitly selected microphone and uses the configured transcription endpoint | Network service; requires the user's service configuration and offline lock disabled |
| Strict-offline browser TTS | Selects a voice the browser reports as local | Only installed/exposed voices are available; no promised voice identity or quality |
| Browser TTS with offline lock disabled | Uses the selected/available browser voice | Some voices can be remote services |
| Configured API TTS | Uses the explicitly configured speech endpoint/model/voice | Separate online service; not a bundled offline feature |

The microphone picker can select an exact input for the API recorder. Browser and on-device recognition use the microphone selected by the browser or OS; this app cannot portably direct those APIs to a particular device. A disconnected selected input is shown as unavailable rather than silently substituted. Reconnect/change settings, then explicitly restart capture.

Camera and microphone controls are independent. Stopping the camera does not end an independently started microphone. Stop, settings changes, device removal, session exit, and save-and-learn cancellation must not unexpectedly restart either device. Pending permissions and late recognition results are guarded against stale sessions.

Browser-recognition voice sessions offer best-effort automatic interruption and echo filtering. Simultaneous playback/recognition depends on browser support; headphones reduce echo. API recorder mode uses explicit Interrupt while the assistant thinks or speaks. A synthetic successful interruption test is not evidence of reliable turn-taking with a real microphone and speaker.

## Evidence

`tests/upgrade_lifecycle_voice_quality.cjs`, `tests/upgrade_lifecycle_media.cjs`, and related recovered media/voice suites check deterministic lifecycle behavior with test doubles. Their final receipt must name the frozen release HTML. They cover interrupted starts, device-list races/disconnects, manual and distinct-speech interruption, self-echo filtering, late-result rejection, speech failure/recovery, and session save/exit boundaries.

No real microphone, speaker, browser speech service, live browser rendering, or physical-device acoustic test was run in this work. See [RADEON_TEST_PLAN.md](RADEON_TEST_PLAN.md) for the remaining local qualification procedure.
