# Journal Entry Flow

## User Flow

1. User opens journal → right page (page 1 front) is the writing area
2. User writes → clicks "Save Entry ✉" → entry POSTed, VADER analyzes, letter generated
3. Envelope overlay appears with wax seal and hint text

### Path A — User opens the envelope
- Clicks envelope → seal cracks, flap folds back, letter rises out
- Clicks letter → full letter modal opens
- Closes modal → envelope closing animation plays in reverse (letter lowers → flap closes → seal reappears → overlay fades out) → journal flips to next page

### Path B — User skips
- Clicks "skip for now" → overlay instantly fades out → journal flips to next page

---

## Envelope Closing Animation Sequence (when envelope was opened)

| Timestamp | Action |
|-----------|--------|
| t=0ms | Letter starts lowering back |
| t=600ms | Letter disappears |
| t=700ms | Flap shadow reappears |
| t=900ms | Flap closes (rotates back) |
| t=2000ms | Shadow gone, wax seal reappears |
| t=2400ms | Overlay fades out, then after 350ms the journal page flips |
