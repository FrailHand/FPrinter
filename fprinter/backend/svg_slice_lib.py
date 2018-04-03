import xml.etree.ElementTree


def parse_svg(file_name):
    try:
        svg_parser = xml.etree.ElementTree.ElementTree(file=file_name)
    except xml.etree.ElementTree.ParseError:
        print('ERROR: invalid svg syntax')
        return

    if svg_parser.findall("{http://www.w3.org/2000/svg}g")[0].get(
            '{http://slic3r.org/namespaces/slic3r}z') is None:
        print('ERROR: svg is not slic3r generated')
        return

    slices_svg = []

    height = svg_parser.getroot().get('height')
    width = svg_parser.getroot().get('width')

    for i in svg_parser.findall("{http://www.w3.org/2000/svg}g"):
        svg_slice = xml.etree.ElementTree.Element('{http://www.w3.org/2000/svg}svg')
        svg_slice.set('height', ''.join((height, 'mm')))
        svg_slice.set('width', ''.join((width, 'mm')))

        svg_slice.set('viewBox', ''.join(('0 0 ', width, ' ', height)))
        svg_slice.set('style', 'background-color:black;fill:white;')
        svg_slice.append(i)

        slices_svg.append(svg_slice)

    total_height = float(slices_svg[-1].getchildren()[-1].get('{http://slic3r.org/namespaces/slic3r}z'))

    return slices_svg, total_height


def check_valid_slic3r_svg(file):
    """
    Checks for valid slic3r generated svg
    :param file_name:
    :return: 0 if OK, -1 if invalid svg, -2 if valid svg but not slic3r generated
    """

    try:
        svg_parser = xml.etree.ElementTree.ElementTree(file=file)
    except xml.etree.ElementTree.ParseError:
        return -1

    if svg_parser.findall("{http://www.w3.org/2000/svg}g")[0].get(
            '{http://slic3r.org/namespaces/slic3r}z') is None:
        return -2

    return 0
