from lxml import etree
from nltk.corpus import framenet
import datetime
import verbnet

VNFN_LOC = "semlink/vn-fn.s"
VN_LOC = "../vn3.3.1-test"

vn = verbnet.VerbNetParser(directory=VN_LOC)
possible_classes = {"-".join(c.split("-")[1:]): [m.name for m in vn.verb_classes_dict[c].members] for c in
                    vn.verb_classes_dict}

possible_frames = {}
for lu in framenet.lus():
    if lu.frame.name not in possible_frames:
        possible_frames[lu.frame.name] = [lu.lexemes[0].name]
    else:
        possible_frames[lu.frame.name].append(lu.lexemes[0].name)


for k in sorted(list(possible_frames.keys())):
    print (k, possible_frames[k])

class Mapping():
    def __init__(self, member, vn_class, fn_frame):
        self.member = member
        self.vn_class = vn_class
        self.fn_frame = fn_frame
        self.errors = self.verify()

    def __str__(self):
        return self.member + " " + self.vn_class + " " + self.fn_frame

    def __eq__(self, other):
        return self.member == other.member and self.vn_class == other.vn_class and self.fn_frame == other.fn_frame

    def __lt__(self, other):
        if self.vn_class == other.vn_class:
            return self.member < other.member
        return self.vn_class < other.vn_class

    def __gt__(self, other):
        if self.vn_class == other.vn_class:
            return self.member > other.member
        return self.vn_class > other.vn_class

    def __hash__(self):
        return hash(self.member) * hash(self.vn_class) * hash(self.fn_frame)

    def as_xml(self):
        out_node = etree.Element("vncls", attrib={"class":self.vn_class, "fnframe":self.fn_frame, "vnmember":self.member, "versionID":"vn3.3"})
        return out_node

    def verify(self):
        res = []
        if self.vn_class.split("-")[0] not in possible_classes.keys():
            res.append("class doesn't exits")
        elif self.member not in possible_classes[self.vn_class.split("-")[0]]:
            res.append("verb not in class")
        if self.fn_frame not in possible_frames.keys():
            res.append("frame doesn't exist")
        elif self.member not in possible_frames[self.fn_frame]:
            res.append("verb not in frame")
        return res


def load_mappings(mapping_file=VNFN_LOC, as_dict=False):
    if not as_dict:
        mappings = []
    else:
        mappings = {}
    tree = etree.parse(open(mapping_file))
    root = tree.getroot()

    for e in root:
        if not as_dict:
            mappings.append(Mapping(e.attrib["vnmember"], e.attrib["class"], e.attrib["fnframe"]))
        else:
            mappings[e.attrib["vnmember"] + ":" + e.attrib["class"]] = e.attrib["fnframe"]

    return mappings


def write_mappings(mappings, output_file):
    root = etree.Element('verbnet-framenet_MappingData', attrib={"date": str(datetime.datetime)})

    for m in mappings:
        root.append(m.as_xml())
    out_str = etree.tostring(root, pretty_print=True)
    with open(output_file, 'wb') as output:
        output.write(out_str)


'''
ms = load_mappings()

errors = {}
for m in ms:
    er_str = " ".join(m.errors)
    if er_str in errors:
        errors[er_str].append(m)
    else:
        errors[er_str] = [m]

for k in errors:
    if k:
        write_mappings(sorted(set(errors[k])), output_file="semlink/errors/" + "_".join(k.split()))
        '''