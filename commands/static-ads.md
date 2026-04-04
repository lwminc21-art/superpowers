---
description: Generate static ad layouts for Meta or paid social. Trigger when user asks for static ads, static creatives, image ads, Facebook ads, ad designs, or says "make me static ads." Also trigger when user provides a reference ad image and asks for variations.
---
# Static Ad Layout Generator
You create production-ready static ad layouts as HTML files that can be screenshotted and uploaded to Meta, TikTok, or any paid social platform.
## Process
1. Identify the reference ad (image file, description, or URL) and brand kit details
2. If no brand kit file exists, ask for: primary color (hex), secondary color (hex), font preference, and logo file path
3. If persona profiles exist in the project, load them
4. Generate each ad as a self-contained HTML file with inline CSS
5. Each ad targets a different persona or angle with unique copy
## Technical Requirements
- Each ad is a single HTML file with all CSS inline
- Default dimensions: 1080x1080px (square) — adjust if user specifies
- Use Google Fonts via CDN link
- All text is real text (not images of text) so it's editable
- Background colors, gradients, and shapes via CSS
- Product photos and logos referenced via relative file path
## Ad Structure
Each HTML file includes:
- **Headline hook** — primary attention-grabbing text (large, prominent)
- **Supporting copy** — 1-2 reinforcing lines (smaller)
- **Product image area** — positioned prominently
- **Logo** — small, typically bottom corner
- **CTA button or badge** — "Shop Now," "Learn More," or custom
- **Brand colors** applied consistently
## Output
Create folder `static-ads-[date]/` containing:
- Individual HTML files: `ad-[number]-[persona/angle].html`
- README.md listing each ad with its target persona, hook, and angle
- Minimum 10 ads unless user specifies otherwise
## Rules
- Each ad gets unique copy — never the same headline on different backgrounds
- Headlines: 3-8 words maximum
- Supporting copy: 1 short sentence
- Copy specific to the persona/angle, not generic
- Match reference ad layout if provided; otherwise use clean modern DTC layout
- Save all files in project folder under static-ads-[date]/
