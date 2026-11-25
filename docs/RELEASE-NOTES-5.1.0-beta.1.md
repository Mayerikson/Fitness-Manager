# Fitness Manager 5.1.0-beta.1

## User-visible changes

- Text and audio are now specified as equal input modes, with a mandatory interpretation preview and explicit confirmation.
- Telegram voice/audio messages can be transcribed locally when the optional faster-whisper dependency is installed.
- The original audio is held in a temporary directory and deleted after transcription.
- The bot shows the recognized transcript and structured candidate before saving.
- Common Portuguese spoken numbers are normalized for supported weight, waist, running, and workout patterns.
- Unsupported or ambiguous speech does not create a health record.
- Confirmed voice records retain `telegram_voice` provenance.

## Install optional speech recognition

```powershell
pip install -r requirements-audio.txt
```

The default model is `base`, CPU `int8`, Portuguese. Model weights may be downloaded on first use and cached locally. Once cached, transcription is local and does not require a paid transcription API. The actual speed and accuracy depend on hardware, model size, recording quality, and background noise.

## Telegram limits

- Maximum audio size: 15 MB.
- Maximum duration: 5 minutes.
- Sender allowlist and private chat checks happen before media download.
- No health record is written until the user confirms `/confirmar ID`.

## Not included yet

- Browser microphone capture in the PWA.
- Native Android/iOS application.
- Offline mobile audio queue.
- Authenticated local HTTP API for mobile synchronization.
- Cloud transcription. It remains disabled by default and is not required.

## Verification

- 39 automated tests passed.
- Release hygiene audit passed.
- The actual faster-whisper model was not downloaded or benchmarked in this build environment; transcription adapter behavior was tested with a mocked model. Validate model installation and performance on the target PC before relying on voice registration.
