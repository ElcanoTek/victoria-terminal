# Signing and Notarization Guide

This guide explains how to sign and notarize the Victoria desktop builds on macOS and Windows, both locally and in GitHub Actions.

## 1. Certificates and Accounts

### macOS
1. Enroll in the [Apple Developer Program](https://developer.apple.com/programs/).
2. In Keychain Access, request a **Developer ID Application** certificate (and an optional **Developer ID Installer** certificate if you later build `.pkg` installers).
3. Create an app-specific password or API key for `notarytool` and note your Team ID.

### Windows
1. Purchase an Authenticode code-signing certificate from a trusted CA (EV certificates build reputation fastest).
2. Export the certificate as a password-protected `.pfx` file.

Store these certificates securely. For GitHub Actions, convert the certificates to Base64 so they can be stored as secrets.

## 2. Local Build Overview

The repository ships helper scripts to create release artifacts:
- `scripts/package_mac.sh` builds a `.app` bundle and zips it for distribution【F:scripts/package_mac.sh†L1-L51】
- `scripts/package_win.bat` creates a one-file EXE and an installer via Inno Setup【F:scripts/package_win.bat†L1-L21】

## 3. macOS: Sign and Notarize Locally

1. **Build the app**
   ```bash
   bash scripts/package_mac.sh
   ```
   This produces `dist/Victoria.app` and `Victoria.app.zip`.
2. **Sign every code object** (the app bundle and any bundled tools such as `crush`).
   ```bash
   codesign --deep --force --options runtime \
     --sign "Developer ID Application: YOUR NAME (TEAMID)" dist/Victoria.app
   ```
3. **(Optional) Sign the DMG** if you create one:
   ```bash
   hdiutil create -volname Victoria -srcfolder dist/Victoria.app Victoria.dmg
   codesign --force --sign "Developer ID Application: YOUR NAME (TEAMID)" Victoria.dmg
   ```
4. **Notarize** the zipped app or signed DMG:
   ```bash
   xcrun notarytool submit Victoria.app.zip \
     --apple-id your-apple-id@example.com \
     --team-id TEAMID \
     --password app-specific-password \
     --wait
   ```
5. **Staple** the ticket:
   ```bash
   xcrun stapler staple dist/Victoria.app
   ```
6. **Verify** Gatekeeper acceptance:
   ```bash
   spctl --assess --type execute --verbose dist/Victoria.app
   ```

## 4. Windows: Sign Locally

1. **Build the binaries**
   ```powershell
   scripts\package_win.bat
   ```
   This creates `dist\Victoria.exe` and `dist\VictoriaSetup.exe`.
2. **Sign each binary and the installer**
   ```powershell
   signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 \
       /f path\to\cert.pfx /p YOUR_PFX_PASSWORD dist\Victoria.exe
   signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 \
       /f path\to\cert.pfx /p YOUR_PFX_PASSWORD dist\VictoriaSetup.exe
   ```
3. **Verify signatures**
   ```powershell
   signtool verify /pa dist\VictoriaSetup.exe
   ```

## 5. Managing Dependencies

- Vendored tools (e.g., `crush`, Python, shared libraries) must be signed individually before `codesign` or `signtool` signs the outer bundle.
- Pin Python packages using `uv` to ensure deterministic builds; the packaging scripts already install requirements via `uvx`【F:scripts/package_mac.sh†L9-L17】【F:scripts/package_win.bat†L11-L19】.

## 6. Automating in GitHub Actions

1. **Store secrets**
   - `APPLE_CERT_P12` – Base64-encoded `.p12` certificate
   - `APPLE_CERT_PASSWORD`
   - `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_NOTARY_PASSWORD`
   - `WIN_CERT_PFX` – Base64-encoded `.pfx` certificate
   - `WIN_CERT_PASSWORD`
2. **macOS job** (add after the build step):
   ```yaml
   - name: Import signing certificate
     run: |
       echo "$APPLE_CERT_P12" | base64 --decode > $HOME/cert.p12
       security create-keychain -p temppass build.keychain
       security import $HOME/cert.p12 -k build.keychain -P "$APPLE_CERT_PASSWORD" -T /usr/bin/codesign
       security set-key-partition-list -S apple-tool:,apple: -s -k temppass build.keychain
       security default-keychain -s build.keychain
   - name: Sign app
     run: |
       codesign --deep --force --options runtime \
         --sign "Developer ID Application: NAME (TEAMID)" dist/Victoria.app
   - name: Notarize app
     run: |
       xcrun notarytool submit Victoria.app.zip \
         --apple-id "$APPLE_ID" --team-id "$APPLE_TEAM_ID" \
         --password "$APPLE_NOTARY_PASSWORD" --wait
   - name: Staple ticket
     run: xcrun stapler staple dist/Victoria.app
   ```
3. **Windows job** (add after building):
   ```yaml
   - name: Import signing certificate
     run: |
       echo "%WIN_CERT_PFX%" | base64 -d > %TEMP%\win.pfx
       certutil -f -p "%WIN_CERT_PASSWORD%" -importpfx %TEMP%\win.pfx
   - name: Sign binaries
     run: |
       signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 \
           /a dist\Victoria.exe
       signtool sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 \
           /a dist\VictoriaSetup.exe
     shell: pwsh
   ```
4. The rest of the existing workflow uploads the signed artifacts and publishes the release【F:.github/workflows/build-release.yml†L31-L91】.

## 7. Verification for Users

Publish SHA-256 checksums and instruct users to run:
```bash
spctl --assess --type execute --verbose Victoria.app
```
```powershell
signtool verify /pa VictoriaSetup.exe
```

Following these steps will produce signed and notarized builds that launch without Gatekeeper or Windows Defender warnings.

