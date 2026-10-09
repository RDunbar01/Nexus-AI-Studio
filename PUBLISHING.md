# Publication boundaries

This work prepares local release artifacts and source/tests/docs. It does not publish a website, push code, create a remote repository/release, configure credentials, accept new model licenses, or upload model files.

The runtime release is `NexusAI.html` with the exact whitelisted expression `assets/` and `licenses/`. General vision packs and language-model checkpoints are excluded. The source/test package may contain explicitly labeled tiny synthetic fixtures and public configuration/tokenizer metadata required for reproduction, not complete pretrained language-model weights. See [RELEASE_PACKAGING.md](RELEASE_PACKAGING.md).

Before any separate authorized publication, inspect the archive inventory for private files/paths, preserve third-party notices/provenance, and choose an appropriate application-code license. The package currently declares `UNLICENSED`; a “free local assistant” description does not grant an open-source or blanket commercial-use license. Runtime/model license declarations do not by themselves clear all training-data or deployment rights.

No release URL exists merely because a local ZIP was created. Report a remote link only after the exact artifact has been uploaded through an authorized workflow and verified at that destination.
