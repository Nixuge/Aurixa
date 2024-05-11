# Aurixa
A heavily Silica inspired tool to make repos for your iOS packages.

# Usage
- Install the latest Python version (if possible at least 3.11+)
- Create a "packages" folder in repo/ if it's not already there
- inside, create a folder for every package you have
- place the files you want like specified in the file "packages" file structure below (as specified, the required files will be created when you run the program anyways and the icons/banners/screenshots are optional, you only need to provide some debs.)
- Run the main file (python src/main.py) and follow the instructions
- Once you're all done, simply upload the "www" folder somewhere (or follow the "Github Pages" instructions below) and you're all good.

# File structures
### Whole repo
```bash
.
└── repo
    ├── packages
    │   └── <see below>
    ├── settings.json
    └── styles
        ├── 404.jinja
        ├── add.jinja
        ├── default.png
        ├── default_tweak_assets
        │   ├── banner.png
        │   └── icon.png
        ├── default.xcf
        ├── index.css
        ├── index.jinja
        ├── index.js
        └── tweak.jinja
```
### Packages
```bash
packages
├── <Package name>
│   ├── <package v1.0>.deb
│   ├── <package v1.1>.deb
│   ├── <package v2.0>.deb
│   └── meta
│       ├── banner.png (optional)
│       ├── changelog.json (created on run)
│       ├── description.md (created on run)
│       ├── icon.png (optional)
│       ├── info.json (created on run)
│       └── screenshots (optional)
│           ├── 01.png
│           ├── 02.png
│           ├── 03.png
│           └── 04.png
└── <Other package>...

```

# Github Pages
- Install `gh` and `git` on your pc
- login to github by running `gh auth login`
- set your git name by running `git config --global user.name "YOUR NAME"`
- set your git EMAIL by running `git config --global user.name "YOUR EMAIL@example.com"`
- Open github in your browser & create a new repo
- Open its "Settings" page & go to the "Pages" tab on the left
- Under "branch", set the branch to "main" and the path to "/ (root)" which should be the default
- Go back to your repo's index
- Copy its url (ending by .git) using the big green "Code" button
- If not already setup, run the setup & use that url when it asks you about a git repo, otherwise paste that url between quotes in the repo/settings.json file at the "git_repo" key (eg: replace `"git_repo": None,` to `"git_repo": "https://github.com/Nixuge/cydia-repo.git",`)
- Should be all good. If you have issues, make sure you're logged in to github on your pc (using the `gh` command), that you have your git name/email set (check google)

Note that you can also use your personal domain. For that, it should be in the same tab as step 6, under "Custom domain". Everything depends on your provider, but you can easily find tutorials about that online/dm me for help about it.

## Why not Silica?
While Silica itself works fine from an user perspective (w some rough edges but it's fine), its code structure is pretty horrible.

On top of that, the rare PRs that are there aren't getting merged, even absolutely NECESSARY ONES (rootless packages support). Even if not merging them was for valid reasons, not having support for that is unacceptable and makes the tool look abandonned.

There are also some limitations (the biggest one for me is that you can't have multiple versions of a single package on a repo which is game changer) that'd take some quite big changes to get working.

## Credits
For now most assets under repo/styles are, altho modified, from Silica.

## TODOs
- Silica-like api/ folder
- help native depiction
- way to add custom depictions yourself
- allow changing more repo settings (version, architectures (of which if possible auto detect all archs from packages & set the necessary ones))
- Windows (lol)
- (unsure) like Silica, add support to replace arbitrary properties in the control file from the json
- (unsure) like Silica, allow adding DEBIAN scripts (postinst, prerm, ...)
- write more detailed README
- (unsure) nicer actual CLI
- Better error handling in some parts (eg loading the repo config)
- Better setup system (allow questions to interact w previous ones, eg the "auto git" one, if set ask if want a prompt or auto commit (for now prompy only))
- (unsure) commit repo that lists changes.
