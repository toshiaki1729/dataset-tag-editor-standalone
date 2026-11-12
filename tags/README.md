# Tag autocomplete data

`danbooru.csv` is the booru tag database used by the built-in tag autocompletion
(Settings → "Enable booru tag autocompletion..."). It is consumed by
`javascript/tag_autocomplete.js` via the `/dte/tagcomplete/tags.csv` endpoint.

## Format

The file uses the CSV format of
[DominikDoom/a1111-sd-webui-tagcomplete](https://github.com/DominikDoom/a1111-sd-webui-tagcomplete):

```
<name>,<type>,<postCount>,"<alias1,alias2,...>"
```

`type` selects the suggestion colour: `0` general, `1` artist, `3` copyright,
`4` character, `5` meta.

## Source & licence

`danbooru.csv` and `extra-quality-tags.csv` are taken from the
`a1111-sd-webui-tagcomplete` project (Copyright (c) 2022 Dominik Reh), which is
released under the **MIT License**. The tag names/counts are derived from
Danbooru. See the upstream repository for the full licence text.

## Using your own tag file

You can point the **"Tag autocomplete CSV file"** setting at any tagcomplete-format
CSV — for example the `tags/e621.csv` or a custom/translation file from an existing
tagcomplete installation. Leave it empty to use the bundled `tags/danbooru.csv`.
Relative paths are resolved against the repository root.
