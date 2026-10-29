# Scan Camera + Signature / Stamp — offline prototype

Open `scan_camera.html` locally in a browser supporting camera access from localhost or HTTPS. No network requests are made by this page. Click Start camera (permission required), Capture page, then drag rectangles around handwritten signatures and ink stamps. Export the original PNG and separate JSON region coordinates. Neither file is uploaded or committed automatically.

**Security**: Do not publish customer scans or annotation JSON. Camera starts only after a user gesture; Stop and page exit release the camera. Captured images and regions are in memory until saved explicitly. Browser downloads are user-initiated. No digital signature verification, stamp authenticity checking, OCR, automatic object detection, document enhancement, or PDF generation. All manually marked regions are `MANUAL_UNVERIFIED`. Do not mistake a picture of a signature or stamp for proof of authority.

**Acceptance gate**: Browser hardware-camera test on user's actual device, permission handling, legibility, multi-page workflow, offline behavior and accessibility still need independent validation. PRODUCTION=HOLD.
