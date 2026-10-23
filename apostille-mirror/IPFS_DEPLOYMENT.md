# IPFS DEPLOYMENT SCRIPT

## CASE-MACHERET-1997-2026

---

## 1. PREPARE FILES FOR IPFS

### File List (ready for pinning)

```bash
# Core Documents
ECHR_complaint_filled.md
UN_JUS_COGENS_PROTOCOL.md
UN_COMMUNICATION_SHORT.md
TUNNEL_PREPARATION.md
apostila.pdf
Jus.Cogens.Q.signed.pdf
МЕМОРАНДУМ О НАРУШЕНИИ JUS COGENS.подписан.pdf
```

---

## 2. IPFS DEPLOYMENT COMMANDS

### Option A: Using IPFS CLI (if installed)

```bash
# Install IPFS if needed
# https://docs.ipfs.io/install/

# Add files to IPFS
ipfs add -r /path/to/documents/

# Pin for persistence
ipfs pin add <CID>

# Get gateway URL
echo "https://ipfs.io/ipfs/<CID>"
```

### Option B: Using Web3.storage (Recommended)

```bash
# 1. Go to https://web3.storage/
# 2. Create account (free)
# 3. Upload files via web interface
# 4. Get IPFS CIDs
```

### Option C: Using Pinata (Recommended)

```bash
# 1. Go to https://www.pinata.cloud/
# 2. Create account
# 3. Upload files
# 4. Get IPFS CIDs
```

---

## 3. MANUAL UPLOAD (No CLI needed)

### Steps:

1. **Go to:** https://www.pinata.cloud/
2. **Sign Up** (free tier: 1GB)
3. **Upload:**
   - ECHR_complaint_filled.md
   - UN_JUS_COGENS_PROTOCOL.md
   - Apostilles (PDFs)
4. **Copy IPFS CIDs**
5. **Update README with links**

---

## 4. DEPLOYMENT CHECKLIST

- [x] Files organized in /ipfs-ready folder
- [ ] Account created on Pinata/Web3.storage
- [ ] Files uploaded
- [ ] CIDs recorded
- [ ] Gateway links tested
- [ ] README updated

---

## 5. AFTER DEPLOYMENT

Update `index.html` with IPFS links:

```html
<a href="https://ipfs.io/ipfs/<YOUR_CID>">View on IPFS</a>
```

---

## 6. QUICK START (Browser Only)

### No installation needed:

1. **Pinata:** https://www.pinata.cloud/
2. **NFT.Storage:** https://nft.storage/
3. **Web3.Storage:** https://web3.storage/

### Upload Process:

1. Create account
2. Drag & drop files
3. Copy IPFS link
4. Share link

---

## 7. IPFS CID MAPPING

| File                      | SHA256 Hash (Integrity)                                            | Status             | CID (Pending) |
| ------------------------- | ------------------------------------------------------------------ | ------------------ | ------------- |
| ECHR_complaint_filled.md  | 1E48D93BB2E31A7217F201474D3995FB586DE3BF2BA76D435566E123665FBDCA | READY_FOR_UPLOAD   | [PENDING]     |
| UN_JUS_COGENS_PROTOCOL.md | 50CDF71ECA01B4917FE26C49E8663378158EE89C85D48C39A6DE81D34C166B70 | READY_FOR_UPLOAD   | [PENDING]     |
| UN_COMMUNICATION_SHORT.md | 3EBFDE871FE8C098F1BB7B43E260B8D8AFF2B357A4330B02E3A9D0532D18E24E | READY_FOR_UPLOAD   | [PENDING]     |
| ECHR_FORM_PREPARED.md     | 9BE155B21FBE36D3B4379B33C0909E3B37F1F5307CEA08E05BB211E2B8DD2852 | READY_FOR_UPLOAD   | [PENDING]     |
| TUNNEL_PREPARATION.md     | E701131A3DB8E9C519FB6D87B02C5F723C5C8377820A54DC1401B0E594A79AF5 | READY_FOR_UPLOAD   | [PENDING]     |
| A©tor_PGP_PublicKey.asc   | 1A3AA84C6D4C74166E8A74B36783D6A2580C3AD38F63E69072C227DE786003F2 | READY_FOR_UPLOAD   | [PENDING]     |

---

## 8. GATEWAY ALTERNATIVES

If ipfs.io is slow:

- https://dweb.link/
- https://gateway.pinata.cloud/
- https://cloudflare-ipfs.com/

---

## 9. BACKUP: BLOCKCHAIN TIMESTAMPING

### Using OriginStamp:

1. Go to https://originstamp.com/
2. Upload files
3. Get blockchain proof
4. Add to evidence

---

## STATUS: READY FOR IPFS UPLOAD

**Next Action:**

1. Go to https://www.pinata.cloud/
2. Upload files from /mnt/c/Users/arhiv/Downloads/
3. Get CIDs

---

_Generated: 02.03.2026_
