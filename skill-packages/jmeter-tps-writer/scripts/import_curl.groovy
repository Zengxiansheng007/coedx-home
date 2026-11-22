import groovy.json.JsonSlurper
import org.apache.jmeter.util.JMeterUtils
import org.apache.jmeter.save.SaveService
import org.apache.jmeter.protocol.http.curl.BasicCurlParser
import org.apache.jmeter.protocol.http.gui.action.ParseCurlCommandAction
import org.apache.jmeter.protocol.http.control.CookieManager
import org.apache.jorphan.collections.ListedHashTree
import org.apache.jorphan.collections.HashTree
import javax.swing.JCheckBox

JMeterUtils.setJMeterHome(args[0])
JMeterUtils.loadJMeterProperties(args[0] + '/bin/jmeter.properties')
JMeterUtils.initLocale()
assert JMeterUtils.getJMeterVersion() == '5.6.3'
def importer = new ParseCurlCommandAction()
def option = importer.class.getDeclaredField('uploadCookiesCheckBox')
option.accessible = true
option.set(importer, new JCheckBox('', true))
def request = importer.class.getDeclaredMethod('createHttpRequest', BasicCurlParser.Request, HashTree, String)
def cookies = importer.class.getDeclaredMethod('createCookieManager', CookieManager, BasicCurlParser.Request)
request.accessible = true
cookies.accessible = true
def tree = new ListedHashTree()
new JsonSlurper().parse(System.in, 'UTF-8').eachWithIndex { command, i ->
    def capture = new BasicCurlParser().parse(command)
    def sampler = request.invoke(importer, capture, tree, 'Writer')
    sampler.name = String.format('T%02d', i+1)
    def manager = new CookieManager()
    cookies.invoke(importer, manager, capture)
    if (manager.cookieCount) {
        manager.setProperty('TestElement.gui_class','org.apache.jmeter.protocol.http.gui.CookiePanel')
        manager.name = '抓包 Cookie'
        tree.getTree(sampler).add(manager)
    }
}
new File(args[1]).withOutputStream { SaveService.saveTree(tree, it) }
