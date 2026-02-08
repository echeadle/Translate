# Document with Images Example

This example demonstrates image embedding in md2pdf.

## Architecture Diagram

Below is a sample architecture diagram:

![Sample Architecture](../../tests/fixtures/images/sample.png)

## Multiple Images

You can include multiple images in a single document:

![First Image](../../tests/fixtures/images/sample.png)

![Second Image](../../tests/fixtures/images/diagram.jpg)

## Text Flow

Images integrate seamlessly with your text. The content flows naturally around them.

## Converting This Example

To convert this example to PDF:

```bash
uv run md2pdf examples/markdown/with_images_example.md --create-output-dir images-test
```

The PDF will be created in `output/images-test/` with all images embedded.
