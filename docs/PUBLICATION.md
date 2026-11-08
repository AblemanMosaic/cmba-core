# Publication boundary

Version `0.1.0a7` is prepared for publication as an **experimental public
research preview**. Publication does not ratify CMBA as a standard, authenticate
the publisher through self-repeated hashes, establish independent review, or
authorize production use.

The frozen `0.1.0a6` source candidate remains unchanged. This successor adds
repository metadata, public onboarding, a unified agent discovery layer,
contributor test lanes, and publication verification. It must therefore receive
its own source archive, wheel, manifest, hashes, and release receipt.

## Repository owner actions

Before pushing to a public remote:

1. choose the final GitHub owner and repository URL;
2. enable private vulnerability reporting;
3. configure branch protection and required CI checks;
4. review contributor, security, and conduct policies;
5. attach exact release artifacts rather than rebuilding them in the browser;
6. publish the release as an alpha research preview with the stated nonclaims.

Repository URLs are deliberately absent from package metadata until the owner
selects the actual remote. No placeholder URL is treated as release metadata.
