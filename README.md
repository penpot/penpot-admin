[uri_license]: https://www.mozilla.org/en-US/MPL/2.0
[uri_license_image]: https://img.shields.io/badge/MPL-2.0-blue.svg

<h1 align="center">
  <br>
  <img style="width:100px" src="images/logo.svg" alt="PENPOT">
  <br>
  PENPOT ADMIN
</h1>

<p align="center">
    <a href="https://www.mozilla.org/en-US/MPL/2.0" rel="nofollow"><img src="https://camo.githubusercontent.com/3fcf3d6b678ea15fde3cf7d6af0e242160366282d62a7c182d83a50bfee3f45e/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4d504c2d322e302d626c75652e737667" alt="License: MPL-2.0" data-canonical-src="https://img.shields.io/badge/MPL-2.0-blue.svg" style="max-width:100%;"></a>
    <a href="https://tree.taiga.io/project/penpot/" title="Managed with Taiga.io" rel="nofollow">
        <img src="https://camo.githubusercontent.com/4a1d1112f0272e3393b1e8da312ff4435418e9e2eb4c0964881e3680f90a653c/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6d616e61676564253230776974682d54414947412e696f2d3730396631342e737667" alt="Managed with Taiga.io" data-canonical-src="https://img.shields.io/badge/managed%20with-TAIGA.io-709f14.svg" style="max-width:100%;"></a>
</p>

<p align="center">
  <a href="https://penpot.app/"><b>Penpot Website</b></a> •
  <a href="https://community.penpot.app/"><b>Penpot Community</b></a>
</p>

<p align="center">
  <img src="images/main.png" alt="thumbnail">
</p>

This is a **very early-stage** admin application for penpot.

## Getting Started

For a quick examplo on how it can be used, please refer to the [penpot
docker compose][1] file for an example for how it can be used.

You should be aware that this is an ongoing work and should be
considered **EXPERIMENTAL**.

## Important Notes

- This application is built using django admin facilites, so on using it, it will create
  some django related tables on the same database as penpot backend. The database is
  shared between the penpot-admin and penpot-backend.
- The penpot-admin communicates with penpot-backend using plain sockets and PREPL, **do
  not expose PREPL port to the internet**.
- Right now it is in very early stage of development and can be considered a limit MVP
  application that we will going to enhace over time and user feedback/requests. So if you
  found an error or do you miss something, feel free to open an issue.


## License ##

```
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Copyright (c) KALEIDOS INC
```
Penpot and the Penpot Admin are Kaleidos’ [open source projects](https://kaleidos.net/products)

[1]: https://github.com/penpot/penpot/blob/develop/docker/images/docker-compose.yaml
