import Foundation
import AppKit
import Vision
import PDFKit
import ImageIO

func emit(_ value: [String: Any]) {
    let data = try! JSONSerialization.data(withJSONObject: value, options: [.sortedKeys])
    print(String(data: data, encoding: .utf8)!)
}
func recognize(_ image: CGImage, orientation: CGImagePropertyOrientation = .up) throws -> [[String: Any]] {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    request.recognitionLanguages = ["en-US"]
    try VNImageRequestHandler(cgImage: image, orientation: orientation).perform([request])
    return (request.results ?? []).compactMap { observation in
        guard let item = observation.topCandidates(1).first else { return nil }
        return ["text": item.string, "ocrConfidence": item.confidence]
    }
}
do {
    let path = CommandLine.arguments[1]
    if path == "--sample" {
        let size = NSSize(width: 1400, height: 850)
        let image = NSImage(size: size)
        image.lockFocus()
        NSColor.white.setFill(); NSRect(origin: .zero, size: size).fill()
        let lines = ["ACORN DEMO PHARMACY", "SYNTHETIC LABEL - NOT FOR MEDICAL USE", "Patient: Example Person", "Example medicine 10 mg tablets", "Take ONE tablet by mouth at 08:00 every day.", "Keep this label for reference", "For prototype demonstration only"]
        for (i, line) in lines.enumerated() {
            let attrs: [NSAttributedString.Key: Any] = [.font: NSFont.systemFont(ofSize: i == 3 ? 46 : 34, weight: i == 3 ? .bold : .regular), .foregroundColor: NSColor.black]
            (line as NSString).draw(at: NSPoint(x: 65, y: 740 - i * 100), withAttributes: attrs)
        }
        image.unlockFocus()
        let rep = NSBitmapImageRep(data: image.tiffRepresentation!)!
        try rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: CommandLine.arguments[2]))
    } else if let pdf = PDFDocument(url: URL(fileURLWithPath: path)) {
        if pdf.pageCount > 8 { throw NSError(domain: "Acorn", code: 1, userInfo: [NSLocalizedDescriptionKey: "Use a PDF with eight pages or fewer."]) }
        var lines: [[String: Any]] = []
        var usedOCR = false
        for index in 0..<pdf.pageCount {
            guard let page = pdf.page(at: index) else { continue }
            if let text = page.string, text.trimmingCharacters(in: .whitespacesAndNewlines).count > 30 {
                lines += text.components(separatedBy: .newlines).filter { !$0.isEmpty }.map { ["text": $0, "page": index + 1] }
            } else {
                usedOCR = true
                let image = page.thumbnail(of: NSSize(width: 1800, height: 2400), for: .mediaBox)
                if let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) { lines += try recognize(cg).map { $0.merging(["page": index + 1]) { _, new in new } } }
            }
        }
        emit(["lines": lines, "method": usedOCR ? "PDF text + local OCR" : "PDF embedded text"])
    } else if let source = CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil), let cg = CGImageSourceCreateImageAtIndex(source, 0, nil) {
        if cg.width * cg.height > 40_000_000 { throw NSError(domain: "Acorn", code: 2, userInfo: [NSLocalizedDescriptionKey: "Image is too large. Use a smaller image."]) }
        // Phone photos are usually stored sideways with an EXIF orientation tag; Vision needs it to read the text upright.
        let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any]
        let orientation = (properties?[kCGImagePropertyOrientation] as? UInt32).flatMap(CGImagePropertyOrientation.init(rawValue:)) ?? .up
        emit(["lines": try recognize(cg, orientation: orientation), "method": "Apple Vision • local OCR"])
    } else { throw NSError(domain: "Acorn", code: 3, userInfo: [NSLocalizedDescriptionKey: "Cannot read this file. Choose a clear PNG, JPEG or PDF."]) }
} catch {
    emit(["error": error.localizedDescription])
    exit(1)
}
