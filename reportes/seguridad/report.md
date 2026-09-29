# ZAP Scanning Report

ZAP by [Checkmarx](https://checkmarx.com/).


## Summary of Alerts

| Risk Level | Number of Alerts |
| --- | --- |
| High | 0 |
| Medium | 0 |
| Low | 2 |
| Informational | 3 |




## Insights

| Level | Reason | Site | Description | Statistic |
| --- | --- | --- | --- | --- |
| Info | Informational | https://parking-proyect.onrender.com | Percentage of responses with status code 2xx | 6 % |
| Info | Informational | https://parking-proyect.onrender.com | Percentage of responses with status code 4xx | 93 % |
| Info | Informational | https://parking-proyect.onrender.com | Percentage of endpoints with content type application/json | 70 % |
| Info | Informational | https://parking-proyect.onrender.com | Percentage of endpoints with content type text/html | 29 % |
| Info | Informational | https://parking-proyect.onrender.com | Percentage of endpoints with method GET | 100 % |
| Info | Informational | https://parking-proyect.onrender.com | Count of total endpoints | 24    |
| Info | Informational | https://parking-proyect.onrender.com | Percentage of slow responses | 11 % |







## Alerts

| Name | Risk Level | Number of Instances |
| --- | --- | --- |
| Cross-Origin-Resource-Policy Header Missing or Invalid | Low | 3 |
| Unexpected Content-Type was returned | Low | 7 |
| A Client Error response code was returned by the server | Informational | 22 |
| Non-Storable Content | Informational | 5 |
| Re-examine Cache-control Directives | Informational | 3 |




## Alert Detail



### [ Cross-Origin-Resource-Policy Header Missing or Invalid ](https://www.zaproxy.org/docs/alerts/90004/)



##### Low (Medium)

### Description

Cross-Origin-Resource-Policy header is an opt-in header designed to counter side-channels attacks like Spectre. Resource should be specifically set as shareable amongst different origins.

* URL: https://parking-proyect.onrender.com/health
  * Node Name: `https://parking-proyect.onrender.com/health`
  * Method: `GET`
  * Parameter: `Cross-Origin-Resource-Policy`
  * Attack: ``
  * Evidence: ``
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/niveles
  * Node Name: `https://parking-proyect.onrender.com/niveles`
  * Method: `GET`
  * Parameter: `Cross-Origin-Resource-Policy`
  * Attack: ``
  * Evidence: ``
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/openapi.json
  * Node Name: `https://parking-proyect.onrender.com/openapi.json`
  * Method: `GET`
  * Parameter: `Cross-Origin-Resource-Policy`
  * Attack: ``
  * Evidence: ``
  * Other Info: ``


Instances: 3

### Solution

Ensure that the application/web server sets the Cross-Origin-Resource-Policy header appropriately, and that it sets the Cross-Origin-Resource-Policy header to 'same-origin' for all web pages.
'same-site' is considered as less secured and should be avoided.
If resources must be shared, set the header to 'cross-origin'.
If possible, ensure that the end user uses a standards-compliant and modern web browser that supports the Cross-Origin-Resource-Policy header (https://caniuse.com/mdn-http_headers_cross-origin-resource-policy).

### Reference


* [ https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy ](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy)


#### CWE Id: [ 693 ](https://cwe.mitre.org/data/definitions/693.html)


#### WASC Id: 14

#### Source ID: 3

### [ Unexpected Content-Type was returned ](https://www.zaproxy.org/docs/alerts/100001/)



##### Low (High)

### Description

A Content-Type of text/html was returned by the server.
This is not one of the types expected to be returned by an API.
Raised by the 'Alert on Unexpected Content Types' script

* URL: https://parking-proyect.onrender.com/computeMetadata/v1/
  * Node Name: `https://parking-proyect.onrender.com/computeMetadata/v1/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/latest/meta-data/
  * Node Name: `https://parking-proyect.onrender.com/latest/meta-data/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/metadata/instance
  * Node Name: `https://parking-proyect.onrender.com/metadata/instance`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/metadata/v1
  * Node Name: `https://parking-proyect.onrender.com/metadata/v1`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/opc/v1/instance/
  * Node Name: `https://parking-proyect.onrender.com/opc/v1/instance/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/opc/v2/instance/
  * Node Name: `https://parking-proyect.onrender.com/opc/v2/instance/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/openstack/latest/meta_data.json
  * Node Name: `https://parking-proyect.onrender.com/openstack/latest/meta_data.json`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``


Instances: 7

### Solution



### Reference




#### Source ID: 4

### [ A Client Error response code was returned by the server ](https://www.zaproxy.org/docs/alerts/100000/)



##### Informational (High)

### Description

A response code of 422 was returned by the server.
This may indicate that the application is failing to handle unexpected input correctly.
Raised by the 'Alert on HTTP Response Code Error' script

* URL: https://parking-proyect.onrender.com
  * Node Name: `https://parking-proyect.onrender.com`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/
  * Node Name: `https://parking-proyect.onrender.com/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/8518577483984492217
  * Node Name: `https://parking-proyect.onrender.com/8518577483984492217`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/actuator/health
  * Node Name: `https://parking-proyect.onrender.com/actuator/health`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/cajones
  * Node Name: `https://parking-proyect.onrender.com/cajones`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/cajones/
  * Node Name: `https://parking-proyect.onrender.com/cajones/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/cajones/2889964031503234487
  * Node Name: `https://parking-proyect.onrender.com/cajones/2889964031503234487`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/cajones/id_cajon
  * Node Name: `https://parking-proyect.onrender.com/cajones/id_cajon`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/cajones/id_cajon/
  * Node Name: `https://parking-proyect.onrender.com/cajones/id_cajon/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/computeMetadata/v1/
  * Node Name: `https://parking-proyect.onrender.com/computeMetadata/v1/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `421`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/latest/meta-data/
  * Node Name: `https://parking-proyect.onrender.com/latest/meta-data/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `421`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/metadata/instance
  * Node Name: `https://parking-proyect.onrender.com/metadata/instance`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `421`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/metadata/v1
  * Node Name: `https://parking-proyect.onrender.com/metadata/v1`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `421`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/niveles/9166921157060750930
  * Node Name: `https://parking-proyect.onrender.com/niveles/9166921157060750930`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/niveles/id_nivel
  * Node Name: `https://parking-proyect.onrender.com/niveles/id_nivel`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/niveles/id_nivel/
  * Node Name: `https://parking-proyect.onrender.com/niveles/id_nivel/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/niveles/id_nivel/6955661652137276895
  * Node Name: `https://parking-proyect.onrender.com/niveles/id_nivel/6955661652137276895`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/niveles/id_nivel/cajones
  * Node Name: `https://parking-proyect.onrender.com/niveles/id_nivel/cajones`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/niveles/id_nivel/cajones/
  * Node Name: `https://parking-proyect.onrender.com/niveles/id_nivel/cajones/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `422`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/opc/v1/instance/
  * Node Name: `https://parking-proyect.onrender.com/opc/v1/instance/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `421`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/opc/v2/instance/
  * Node Name: `https://parking-proyect.onrender.com/opc/v2/instance/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `421`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/openstack/latest/meta_data.json
  * Node Name: `https://parking-proyect.onrender.com/openstack/latest/meta_data.json`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `421`
  * Other Info: ``


Instances: 22

### Solution



### Reference



#### CWE Id: [ 388 ](https://cwe.mitre.org/data/definitions/388.html)


#### WASC Id: 20

#### Source ID: 4

### [ Non-Storable Content ](https://www.zaproxy.org/docs/alerts/10049/)



##### Informational (Medium)

### Description

The response contents are not storable by caching components such as proxy servers. If the response does not contain sensitive, personal or user-specific information, it may benefit from being stored and cached, to improve performance.

* URL: https://parking-proyect.onrender.com/cajones/id_cajon
  * Node Name: `https://parking-proyect.onrender.com/cajones/id_cajon`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/health
  * Node Name: `https://parking-proyect.onrender.com/health`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/niveles
  * Node Name: `https://parking-proyect.onrender.com/niveles`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/niveles/id_nivel/cajones
  * Node Name: `https://parking-proyect.onrender.com/niveles/id_nivel/cajones`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/openapi.json
  * Node Name: `https://parking-proyect.onrender.com/openapi.json`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``


Instances: 5

### Solution

The content may be marked as storable by ensuring that the following conditions are satisfied:
The request method must be understood by the cache and defined as being cacheable ("GET", "HEAD", and "POST" are currently defined as cacheable)
The response status code must be understood by the cache (one of the 1XX, 2XX, 3XX, 4XX, or 5XX response classes are generally understood)
The "no-store" cache directive must not appear in the request or response header fields
For caching by "shared" caches such as "proxy" caches, the "private" response directive must not appear in the response
For caching by "shared" caches such as "proxy" caches, the "Authorization" header field must not appear in the request, unless the response explicitly allows it (using one of the "must-revalidate", "public", or "s-maxage" Cache-Control response directives)
In addition to the conditions above, at least one of the following conditions must also be satisfied by the response:
It must contain an "Expires" header field
It must contain a "max-age" response directive
For "shared" caches such as "proxy" caches, it must contain a "s-maxage" response directive
It must contain a "Cache Control Extension" that allows it to be cached
It must have a status code that is defined as cacheable by default (200, 203, 204, 206, 300, 301, 404, 405, 410, 414, 501).

### Reference


* [ https://datatracker.ietf.org/doc/html/rfc7234 ](https://datatracker.ietf.org/doc/html/rfc7234)
* [ https://datatracker.ietf.org/doc/html/rfc7231 ](https://datatracker.ietf.org/doc/html/rfc7231)
* [ https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html ](https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html)


#### CWE Id: [ 524 ](https://cwe.mitre.org/data/definitions/524.html)


#### WASC Id: 13

#### Source ID: 3

### [ Re-examine Cache-control Directives ](https://www.zaproxy.org/docs/alerts/10015/)



##### Informational (Low)

### Description

The cache-control header has not been set properly or is missing, allowing the browser and proxies to cache content. For static assets like css, js, or image files this might be intended, however, the resources should be reviewed to ensure that no sensitive content will be cached.

* URL: https://parking-proyect.onrender.com/health
  * Node Name: `https://parking-proyect.onrender.com/health`
  * Method: `GET`
  * Parameter: `cache-control`
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/niveles
  * Node Name: `https://parking-proyect.onrender.com/niveles`
  * Method: `GET`
  * Parameter: `cache-control`
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: https://parking-proyect.onrender.com/openapi.json
  * Node Name: `https://parking-proyect.onrender.com/openapi.json`
  * Method: `GET`
  * Parameter: `cache-control`
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``


Instances: 3

### Solution

For secure content, ensure the cache-control HTTP header is set with "no-cache, no-store, must-revalidate". If an asset should be cached consider setting the directives "public, max-age, immutable".

### Reference


* [ https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html#web-content-caching ](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html#web-content-caching)
* [ https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control ](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control)
* [ https://grayduck.mn/2021/09/13/cache-control-recommendations/ ](https://grayduck.mn/2021/09/13/cache-control-recommendations/)


#### CWE Id: [ 525 ](https://cwe.mitre.org/data/definitions/525.html)


#### WASC Id: 13

#### Source ID: 3


