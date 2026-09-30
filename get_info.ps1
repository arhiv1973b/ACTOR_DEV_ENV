$f = Get-Item -LiteralPath "F:\Мой диск\ACTOR_DEV_ENV\EVIDENCE_REGISTRY_INDEX.json"
[PSCustomObject]@{
    Name = $f.Name
    Length = $f.Length
    Attributes = $f.Attributes
}
