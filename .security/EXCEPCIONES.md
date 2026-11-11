# Excepciones de identificación verificadas — Semana 07

Son correcciones de asociaciones incorrectas, no aceptación de vulnerabilidades ni de riesgo por el usuario. Caducan el 2027-02-10 UTC. No cambian CVSS >= 7, SAST ERROR/HIGH/CRITICAL, analizadores, dependencias de desarrollo ni archivos escaneados. Este archivo y suppressions.xml se congelan antes de la nueva pareja FAILED/SUCCESS.

| ID | Alcance exacto | Evidencia técnica y justificación | Riesgo residual |
|---|---|---|---|
| FP-01 | pkg:npm/grunt-cli, versiones 1.2.0, 1.3.2 y 1.5.0; solo CVE-2017-16058 | El registro CVE describe el paquete malicioso `gruntcli`, sin guion. Los manifiestos instalados declaran `grunt-cli`, repositorio `gruntjs/grunt-cli`, CLI oficial. Son identidades distintas. | No cubre otros CVE ni versiones. Una futura alteración maliciosa de grunt-cli no queda evaluada por esta identificación histórica. |
| FP-02 | pkg:npm/mongodb, versiones 2.2.36 y 3.7.4; CVE-2025-14847, CVE-2026-9753, CVE-2021-32036, CVE-2014-8180 | Los registros CVE afectados son MongoDB Server y su distribución Red Hat Satellite. El paquete npm es el cliente Node.js (`node-mongodb-native`); no contiene el servidor mongod, el motor de agregación, ni los comandos vulnerables del servidor. Sus versiones no son las versiones del servidor. Las vulnerabilidades propias del driver, como GHSA-mh5c-679w-hh4r en 2.2.36, siguen bloqueando y se remedian. | La seguridad de un servidor MongoDB desplegado debe evaluarse por separado. Esta excepción no certifica el servidor ni excluye ningún CVE del driver fuera de los cuatro identificadores enumerados. |
| FP-03 | Solo el archivo con SHA-1 287f8835f51b6392917f423f48e2e38a58e64804, gaze/lib/helper.js; CVE-2019-10744, CVE-2021-23337, CVE-2018-3721, CVE-2018-16487 | Se conserva la atribución de Lodash 1.0.1, pero solo se copió el algoritmo `unique`. Los 80 renglones y sus seis exportaciones fueron inspeccionados: no contiene `template`, `defaultsDeep`, `merge` ni `mergeWith`, que son los métodos afectados. Una atribución de licencia no equivale a incluir toda la biblioteca. La prueba de exportaciones y el archivo completo se conservan en las evidencias. SHA-256 adicional: addcc6d7dc1b9075a277dfdfc49b21184cc9c351757060313ec3a90784a05ddf. | No se afirma que el helper esté libre de todo defecto: únicamente faltan las implementaciones afectadas por esos cuatro CVE. Si cambian sus bytes deja de coincidir la excepción. No se suprimen copias completas de Lodash. |

Fuentes primarias:
- https://cveawg.mitre.org/api/cve/CVE-2017-16058
- https://github.com/gruntjs/grunt-cli
- https://cveawg.mitre.org/api/cve/CVE-2025-14847
- https://cveawg.mitre.org/api/cve/CVE-2026-9753
- https://cveawg.mitre.org/api/cve/CVE-2021-32036
- https://cveawg.mitre.org/api/cve/CVE-2014-8180
- https://github.com/mongodb/node-mongodb-native
- https://raw.githubusercontent.com/shama/gaze/v1.1.3/lib/helper.js

Las copias completas de Lodash 4.17.21 en los bundles de JSHint sí eran código vulnerable: se sustituyeron por la implementación completa 4.18.1, manteniendo licencias y funcionalidad. No tienen excepción. El archivo local vendor/jshint-2.13.6-s07.tgz conserva la versión de JSHint y su integridad distingue el parche. vendor/jshint-provenance.json y rebuild-jshint.py documentan y reproducen la sustitución; no se alteran solo etiquetas de versión.
