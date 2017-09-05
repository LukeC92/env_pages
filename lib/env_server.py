import tornado.ioloop
import tornado.web

class PackageRow(object):
    row_fmt = """\
        <tr>
            <td>{package}</td>
            <td>{version}</td>
            <td>{build}</td>
        </tr>
        """
    def __init__(self, package, version, build):
        self.package = package
        self.version = version
        self.build = build

    def __str__(self):
        return self.row_fmt.format(
            package=self.package,
            version=self.version,
            build=self.build)


class PackageTable(object):
    table_fmt = """\
        <table id={table_id}>
          <tr>
              <th>Name</th>
              <th>Version</th>
              <th>Build string</th>
          </tr>
          {rows}
        </table>
        """

    def __init__(self, package_data, table_id="package_table"):
        self.rows = package_data
        self.table_id = table_id

    def __str__(self):
        return self.table_fmt.format(
            table_id = self.table_id,
            rows='\n'.join(
                str(row) for row in self.rows))


class PageContent(object):
    def __init__(self, date, platform, env_name, package_table):
        self.date = date
        self.platform = platform
        self.env_name = env_name
        self.package_table = package_table

    html_page_fmt = """\
    <html>
    <style>
        table {{
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid black;
            padding: 10px;
            text-align: left;
        }}
    </style>
    <body>
        <h1>Content of Environment "{platform}/{envname}".</h1>
        <br>
        <h2>Detail:</h2>
        &nbsp; &nbsp; Sample date: {sample_date}
        <br>
        &nbsp; &nbsp; Platform: {platform}
        <br>
        &nbsp; &nbsp; Name: {envname}
        <h2>Content packages:</h2>
        {package_html}
    </body>
    </html>
    """

    def html(self):
        # NOTE: id will be required if CSS or jQuery or Datatables code is
        # applied :  For now, this is not used.
        package_table_id = self.package_table.table_id
        package_html = str(self.package_table)
        result_text = self.html_page_fmt.format(
            sample_date=self.date,
            platform=self.platform,
            envname=self.env_name,
            package_html=package_html,
            package_table_id=package_table_id)
        return result_text


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        text = self.application.content_builder.html()
        self.write(text)


def test_content():
    row1 = PackageRow('a_pkg', '0.2.13', 'py27_0')
    row2 = PackageRow('pkg_ZZZ', '9.99.999', '-')
    pkgs = PackageTable([row1, row2])
    page = PageContent(date='2099-01-01',
                       platform='my_pc',
                       env_name='env_x_1',
                       package_table=pkgs)
    return page


def make_app():
    return tornado.web.Application([
        (r"/envtst", MainHandler),
    ])


def start():
    app = make_app()
    app.content_builder = test_content()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

#tst = test_content()
#print tst.html()


if __name__ == '__main__':
    start()
