# Protected GTM site

Only an unlock shell and encrypted site/source packages are published. Content and downloads require the shared password. Request access from cobrown@ddn.com.

Do not publish the editable source or plaintext exports to this repository. The source recovery package is encrypted with the site password using PBKDF2-SHA256 (600,000 iterations), AES-256-GCM and gzip. Its additional authenticated data is `DDN-GTM-site-v1`; decrypt, gunzip and unzip locally. The site package uses the same format with JSON after decompression. Each package uses an independent random salt and nonce. The password is not in this repository.

Password changes require rebuilding/re-encrypting both packages. Historical content published before this protection remains in Git history; this release does not erase prior public copies. This is password-based content encryption, not individual identity or account management.
