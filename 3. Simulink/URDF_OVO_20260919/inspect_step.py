"""Read a fresh SolidWorks STEP assembly and report its named component tree.

Uses the OCP installation bundled with OVO. Does not modify the CAD document.
"""
import argparse
import json
from pathlib import Path

from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label, TDF_LabelSequence
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ShapeTool


def label_name(label):
    attr = TDataStd_Name()
    if label.FindAttribute(TDataStd_Name.GetID_s(), attr):
        return attr.Get().ToExtString()
    return ""


def read_assembly(path):
    doc = TDocStd_Document(TCollection_ExtendedString("step-inspection"))
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    if reader.ReadFile(str(path)) != IFSelect_RetDone or not reader.Transfer(doc):
        raise RuntimeError(f"STEP import failed: {path}")
    tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    roots = TDF_LabelSequence()
    tool.GetFreeShapes(roots)
    return doc, tool, roots


def describe(label, depth=0):
    referred = TDF_Label()
    ref = XCAFDoc_ShapeTool.GetReferredShape_s(label, referred)
    definition = referred if ref else label
    tr = XCAFDoc_ShapeTool.GetLocation_s(label).Transformation()
    row = {
        "instance_name": label_name(label),
        "definition_name": label_name(definition),
        "location_mm": [[tr.Value(i, j) for j in range(1, 5)] for i in range(1, 4)],
    }
    children = TDF_LabelSequence()
    XCAFDoc_ShapeTool.GetComponents_s(definition, children, False)
    row["children"] = [describe(children.Value(i), depth + 1)
                       for i in range(1, children.Length() + 1)]
    return row


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("step", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    doc, tool, roots = read_assembly(args.step)
    data = [describe(roots.Value(i)) for i in range(1, roots.Length() + 1)]
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload if not args.output else f"{len(data)} root(s); wrote {args.output}")
