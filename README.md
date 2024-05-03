# Aurixa
A heavily Silica inspired tool to make repos for your iOS packages.

## Why not Silica?
While Silica itself works fine from an user perspective (w some rough edges but it's fine), its code structure is pretty horrible.

On top of that, the rare PRs that are there aren't getting merged, even absolutely NECESSARY ONES (rootless packages support). Even if not merging them was for valid reasons, not having support for that is unacceptable and makes the tool look abandonned.

There are also some limitations (the biggest one for me is that you can't have multiple versions of a single package on a repo which is game changer) that'd take some quite big changes to get working.

## Credits
For now most assets under repo/styles are, altho modified, from Silica.

## TODOs
- Sign Release with gpg
- Silica-like api/ folder
- native/help depiction
- way to add custom depictions yourself
- allow changing more repo settings (version, architectures (of which if possible auto detect all archs from packages & set the necessary ones))
- Windows (lol)
- (unsure) like Silica, add support to replace arbitrary properties in the control file from the json
- (unsure) like Silica, allow adding DEBIAN scripts (postinst, prerm, ...)
- write more detailed README
- auto git push
- (unsure) nicer actual CLI
- Better error handling in some parts (eg loading the repo config)