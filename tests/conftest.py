"""Shared test fixtures.

Two flavors of fixture live here:
  * captured tool output (strings) -> feed the *pure* parsers, no binary needed
  * tmp dirs -> isolate filesystem side effects (audit log, reports)

Integration tests that need a real tool guard themselves with, e.g.:
    pytestmark = pytest.mark.skipif(which("pdfinfo") is None, reason="...")
"""
import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to tests/fixtures/ (sample files committed for integration tests)."""
    return FIXTURES


@pytest.fixture
def case_dir(tmp_path) -> Path:
    """An isolated per-test case directory (audit log / reports land here)."""
    d = tmp_path / "case"
    d.mkdir()
    return d


@pytest.fixture
def pdfinfo_clean() -> str:
    """Representative `pdfinfo` stdout for a benign PDF (no JS/encryption).

    Note the colon inside the timestamp value -- the parser must keep it
    (maxsplit=1), so this fixture also guards that regression.
    """
    return (
        "Title:           Shoham Houta\n"
        "Author:          Shoham Houta\n"
        "Creator:         Canva\n"
        "Producer:        Canva\n"
        "CreationDate:    Thu Apr 23 12:40:27 2026 IDT\n"
        "ModDate:         Thu Apr 23 12:40:27 2026 IDT\n"
        "JavaScript:      no\n"
        "Encrypted:       no\n"
        "Suspects:        no\n"
        "Pages:           1\n"
        "Page size:       595.5 x 842.25 pts (A4)\n"
        "PDF version:     1.4\n"
    )


@pytest.fixture
def pdfinfo_lead() -> str:
    """Representative `pdfinfo` stdout for a suspicious PDF (LEAD triggers)."""
    return (
        "Title:           Invoice\n"
        "Author:          attacker\n"
        "Creator:         Microsoft Word\n"
        "Producer:        Skia/PDF\n"
        "JavaScript:      yes\n"
        "Encrypted:       yes\n"
        "Suspects:        yes\n"
        "Pages:           3\n"
    )


@pytest.fixture
def exiftool_clean() -> str:
    """Real `exiftool -j -G` output as a JSON string (matches live stdout)."""
    return json.dumps([{
        "SourceFile": "../IMG_9367.jpeg",
        "ExifTool:ExifToolVersion": 13.55,
        "File:FileName": "IMG_9367.jpeg",
        "File:Directory": "..",
        "File:FileSize": "2.9 MB",
        "File:FileModifyDate": "2026:06:21 23:47:18+03:00",
        "File:FileAccessDate": "2026:06:21 23:47:20+03:00",
        "File:FileInodeChangeDate": "2026:06:21 23:47:19+03:00",
        "File:FilePermissions": "-rw-r--r--",
        "File:FileType": "JPEG",
        "File:FileTypeExtension": "jpg",
        "File:MIMEType": "image/jpeg",
        "File:ExifByteOrder": "Big-endian (Motorola, MM)",
        "File:ImageWidth": 3024,
        "File:ImageHeight": 4032,
        "File:EncodingProcess": "Baseline DCT, Huffman coding",
        "File:BitsPerSample": 8,
        "File:ColorComponents": 3,
        "File:YCbCrSubSampling": "YCbCr4:2:0 (2 2)",
        "JFIF:JFIFVersion": 1.01,
        "JFIF:ResolutionUnit": "inches",
        "JFIF:XResolution": 300,
        "JFIF:YResolution": 300,
        "EXIF:Make": "Apple",
        "EXIF:Model": "iPhone 16 Plus",
        "EXIF:Orientation": "Horizontal (normal)",
        "EXIF:XResolution": 72,
        "EXIF:YResolution": 72,
        "EXIF:ResolutionUnit": "inches",
        "EXIF:Software": "26.3.1",
        "EXIF:ModifyDate": "2026:03:22 14:48:02",
        "EXIF:HostComputer": "iPhone 16 Plus",
        "EXIF:TileWidth": 512,
        "EXIF:TileLength": 512,
        "EXIF:YCbCrPositioning": "Centered",
        "EXIF:ExposureTime": "1/630",
        "EXIF:FNumber": 1.6,
        "EXIF:ExposureProgram": "Program AE",
        "EXIF:ISO": 50,
        "EXIF:ExifVersion": "0232",
        "EXIF:DateTimeOriginal": "2026:03:22 14:48:02",
        "EXIF:CreateDate": "2026:03:22 14:48:02",
        "EXIF:OffsetTime": "+02:00",
        "EXIF:OffsetTimeOriginal": "+02:00",
        "EXIF:OffsetTimeDigitized": "+02:00",
        "EXIF:ComponentsConfiguration": "Y, Cb, Cr, -",
        "EXIF:ShutterSpeedValue": "1/630",
        "EXIF:ApertureValue": 1.6,
        "EXIF:BrightnessValue": 7.339982367,
        "EXIF:ExposureCompensation": 0,
        "EXIF:MeteringMode": "Multi-segment",
        "EXIF:Flash": "Off, Did not fire",
        "EXIF:FocalLength": "6.0 mm",
        "EXIF:SubjectArea": "2014 1509 1105 664",
        "EXIF:SubSecTime": 386,
        "EXIF:SubSecTimeOriginal": 386,
        "EXIF:SubSecTimeDigitized": 386,
        "EXIF:FlashpixVersion": "0100",
        "EXIF:ColorSpace": "Uncalibrated",
        "EXIF:ExifImageWidth": 4032,
        "EXIF:ExifImageHeight": 3024,
        "EXIF:SensingMethod": "One-chip color area",
        "EXIF:SceneType": "Directly photographed",
        "EXIF:ExposureMode": "Auto",
        "EXIF:WhiteBalance": "Auto",
        "EXIF:DigitalZoomRatio": 1.050729673,
        "EXIF:FocalLengthIn35mmFormat": "54 mm",
        "EXIF:SceneCaptureType": "Standard",
        "EXIF:LensInfo": "5.960000038mm f/1.6",
        "EXIF:LensMake": "Apple",
        "EXIF:LensModel": "iPhone 16 Plus back dual wide camera 5.96mm f/1.6",
        "EXIF:CompositeImage": "General Composite Image",
        "EXIF:GPSLatitudeRef": "North",
        "EXIF:GPSLatitude": "31 deg 22' 45.01\"",
        "EXIF:GPSLongitudeRef": "East",
        "EXIF:GPSLongitude": "34 deg 37' 23.26\"",
        "EXIF:GPSAltitudeRef": "Above Sea Level",
        "EXIF:GPSAltitude": "116.1663418 m",
        "EXIF:GPSTimeStamp": "12:48:00",
        "EXIF:GPSSpeedRef": "km/h",
        "EXIF:GPSSpeed": 0.4600000083,
        "EXIF:GPSImgDirectionRef": "Magnetic North",
        "EXIF:GPSImgDirection": 258.8305664,
        "EXIF:GPSDestBearingRef": "Magnetic North",
        "EXIF:GPSDestBearing": 258.8305664,
        "EXIF:GPSDateStamp": "2026:03:22",
        "EXIF:GPSHPositioningError": "3.535533905 m",
        "MakerNotes:MakerNoteVersion": 16,
        "MakerNotes:RunTimeFlags": "Valid",
        "MakerNotes:RunTimeValue": 102592416781375,
        "MakerNotes:RunTimeScale": 1000000000,
        "MakerNotes:RunTimeEpoch": 0,
        "MakerNotes:AEStable": "Yes",
        "MakerNotes:AETarget": 175,
        "MakerNotes:AEAverage": 184,
        "MakerNotes:AFStable": "Yes",
        "MakerNotes:AccelerationVector": "-0.04793481526 -0.5368598699 -0.8326860669",
        "MakerNotes:FocusDistanceRange": "0.07 - 0.50 m",
        "MakerNotes:ImageCaptureType": "Scene",
        "MakerNotes:LivePhotoVideoIndex": 5290036,
        "MakerNotes:LuminanceNoiseAmplitude": 0.006372890437,
        "MakerNotes:PhotosAppFeatureFlags": 1,
        "MakerNotes:HDRHeadroom": 1.00999999,
        "MakerNotes:AFPerformance": "103 1 31",
        "MakerNotes:SignalToNoiseRatio": 48.81890868,
        "MakerNotes:PhotoIdentifier": "86CB6AB1-5652-4A78-9FE0-5F1CBB18BF91",
        "MakerNotes:ColorTemperature": 5637,
        "MakerNotes:CameraType": "Back Normal",
        "MakerNotes:FocusPosition": 71,
        "MakerNotes:HDRGain": 0.009681807835,
        "XMP:XMPToolkit": "XMP Core 6.0.0",
        "XMP:CompositeImage": 2,
        "XMP:DateCreated": "2026:03:22 14:48:02+02:00",
        "XMP:ModifyDate": "2026:03:22 14:48:02",
        "XMP:CreateDate": "2026:03:22 14:48:02",
        "XMP:CreatorTool": "26.3.1",
        "XMP:Subject": "",
        "MPF:MPFVersion": "0100",
        "MPF:NumberOfImages": 3,
        "MPF:MPImageFlags": "(none)",
        "MPF:MPImageFormat": "JPEG",
        "MPF:MPImageType": "Undefined",
        "MPF:MPImageLength": 316023,
        "MPF:MPImageStart": 2613111,
        "MPF:DependentImage1EntryNumber": 0,
        "MPF:DependentImage2EntryNumber": 0,
        "MPF:MPImage2": "(Binary data 35632 bytes, use -b option to extract)",
        "MPF:MPImage3": "(Binary data 316023 bytes, use -b option to extract)",
        "ICC_Profile:ProfileCMMType": "Apple Computer Inc.",
        "ICC_Profile:ProfileVersion": "4.0.0",
        "ICC_Profile:ProfileClass": "Input Device Profile",
        "ICC_Profile:ColorSpaceData": "RGB ",
        "ICC_Profile:ProfileConnectionSpace": "XYZ ",
        "ICC_Profile:ProfileDateTime": "2016:01:01 00:00:00",
        "ICC_Profile:ProfileFileSignature": "acsp",
        "ICC_Profile:PrimaryPlatform": "Apple Computer Inc.",
        "ICC_Profile:CMMFlags": "Not Embedded, Independent",
        "ICC_Profile:DeviceManufacturer": "Apple Computer Inc.",
        "ICC_Profile:DeviceModel": "",
        "ICC_Profile:DeviceAttributes": "Reflective, Glossy, Positive, Color",
        "ICC_Profile:RenderingIntent": "Perceptual",
        "ICC_Profile:ConnectionSpaceIlluminant": "0.9642 1 0.82491",
        "ICC_Profile:ProfileCreator": "Apple Computer Inc.",
        "ICC_Profile:ProfileID": "09a72bcf796cf3543b61a77f1ae38acc",
        "ICC_Profile:ProfileDescription": "Apple Wide Color Sharing Profile",
        "ICC_Profile:ProfileCopyright": "Copyright Apple Inc., 2016",
        "ICC_Profile:MediaWhitePoint": "0.9642 1 0.8251",
        "ICC_Profile:AToB2": "(Binary data 29772 bytes, use -b option to extract)",
        "ICC_Profile:ChromaticAdaptation": "1.04781 0.02289 -0.05017 0.02953 0.99051 -0.01706 -0.00925 0.01506 0.75191",
        "ICC_Profile:AToB0": "(Binary data 29772 bytes, use -b option to extract)",
        "ICC_Profile:AToB1": "(Binary data 29772 bytes, use -b option to extract)",
        "APP10:HDRGainCurveSize": 251,
        "APP10:HDRGainCurve": "(Binary data 1893 bytes, use -b option to extract)",
        "Composite:RunTimeSincePowerUp": "1 days 4:29:52",
        "Composite:Aperture": 1.6,
        "Composite:ImageSize": "3024x4032",
        "Composite:Megapixels": 12.2,
        "Composite:ScaleFactor35efl": 9.1,
        "Composite:ShutterSpeed": "1/630",
        "Composite:SubSecCreateDate": "2026:03:22 14:48:02.386+02:00",
        "Composite:SubSecDateTimeOriginal": "2026:03:22 14:48:02.386+02:00",
        "Composite:SubSecModifyDate": "2026:03:22 14:48:02.386+02:00",
        "Composite:GPSAltitude": "116.1 m Above Sea Level",
        "Composite:GPSDateTime": "2026:03:22 12:48:00Z",
        "Composite:GPSLatitude": "31 deg 22' 45.01\" N",
        "Composite:GPSLongitude": "34 deg 37' 23.26\" E",
        "Composite:CircleOfConfusion": "0.003 mm",
        "Composite:FOV": "36.9 deg",
        "Composite:FocalLength35efl": "6.0 mm (35 mm equivalent: 54.0 mm)",
        "Composite:GPSPosition": "31 deg 22' 45.01\" N, 34 deg 37' 23.26\" E",
        "Composite:HyperfocalDistance": "6.69 m",
        "Composite:LightValue": 11.7,
        "Composite:LensID": "iPhone 16 Plus back dual wide camera 5.96mm f/1.6"
    }])
