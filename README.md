# simple-enum
Making subdomain enumeration great again... or just automating it. Whatever you prefer.

## Requirements
You will need both amass and aquatone downloaded and in your PATH.
* [amass](https://github.com/OWASP/Amass)
    * `go get -u github.com/OWASP/Amass/...`
    * `snap install amass`
* [aquatone](https://github.com/michenriksen/aquatone)
    * `go get -u github.com/michenriksen/aquatone`

## Usage
1. Perform a subdomain enumeration and screenshot everything found
    * `python3 simple_enum.py scan -d <domain> | -df <domain_file>`
2. Perform a subdomain enumeration
    * `python3 simple_enum.py enumerate -d <domain> | -df <domain_file>`
3. Screenshot all domains found via enumeration (only works if subdomain enumeration was previously run)
    * `python3 simple_enum.py capture -d <domain> | -df <domain_file>`

## General Notes
This is still under development, so there may be some issues. File an issue or better yet, create a PR :)
