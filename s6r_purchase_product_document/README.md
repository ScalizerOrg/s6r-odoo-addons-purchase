# Scalizer Purchase Product Document

Share product documents and subcontracting bills of materials with vendors on RFQs and purchase orders.

## Features

- New field _Purchase: Visible at_ on product documents: _Hidden_ (default), _On RFQ only_, _On RFQ and PO_, _On PO
  only_.
- _Documents_ tab and smart button on the purchase order: selection, in the wanted order, of the documents of the
  ordered products to share with the vendor.
- _BoM_ column on the purchase order lines of subcontracted products: subcontracting BoMs of the vendor without project
  or with the project of the order, pre-filled when only one is available, required otherwise, read-only once the
  order is confirmed. The PDF of the BoM is frozen on the order at its confirmation.
- The PDF of the BoMs and the PDF documents shared in the order state are appended to the reports selected in the
  settings (RFQ and purchase order by default).
- The email sent from _Send RFQ_ / _Send PO_ lists the shared documents with a download link, attaches the PDF files
  not appended to the report and gathers the other files in a zip archive.
- _Preview_ button showing the order as the vendor sees it, with a _Documents_ section on the vendor portal. A document
  not shared in the order state can not be downloaded.

## Usage

1. On a product, open the _Documents_ smart button and set _Purchase: Visible at_ on the documents to share.
2. On a purchase order, select the documents in the _Documents_ tab (or from the _Documents_ smart button) and check
   the _BoM_ of the subcontracted products.
3. Print or send the RFQ / purchase order.
4. In _Purchase > Configuration > Settings_, choose the reports including the documents and the report used for the
   subcontracting BoMs (by default a BoM report without costs).

## Authors

- Scalizer

## Contributors

- Julien Hémono ([Github](https://github.com/jhemono))

## Maintainers

This module is maintained by [Scalizer](https://www.scalizer.fr).

![Scalizer](./static/description/logo.png)
