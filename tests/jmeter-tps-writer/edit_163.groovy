import org.apache.jmeter.util.JMeterUtils
import org.apache.jmeter.save.SaveService
import org.apache.jmeter.protocol.http.control.gui.HttpTestSampleGui
import org.apache.jmeter.protocol.http.sampler.HTTPSamplerProxy
import org.apache.jmeter.gui.GuiPackage
import org.apache.jmeter.gui.tree.JMeterTreeModel
import org.apache.jmeter.gui.tree.JMeterTreeListener
import org.apache.jorphan.collections.SearchByClass
import javax.swing.SwingUtilities
import javax.swing.text.JTextComponent
import java.awt.Container

JMeterUtils.setJMeterHome(args[0])
JMeterUtils.loadJMeterProperties(args[0] + '/bin/jmeter.properties')
JMeterUtils.initLocale()
def plan = SaveService.loadTree(new File(args[1]))
def search = new SearchByClass(HTTPSamplerProxy)
plan.traverse(search)
SwingUtilities.invokeAndWait {
    def model = new JMeterTreeModel()
    GuiPackage.initInstance(new JMeterTreeListener(model), model)
    def gui = GuiPackage.getInstance()
    model.addSubTree(plan, model.root.getChildAt(0))
    def editors = []
    model.root.depthFirstEnumeration().each { node ->
        if (node != model.root) {
            def editor = gui.getGui(node.testElement)
            assert editor != null
            editor.configure(node.testElement)
            editors << node.testElement.name
        }
    }
    assert editors.containsAll(['查询指南 [T01]', 'HTTP 请求默认值', 'HTTP 信息头管理器',
                                'HTTP 状态为 2xx', '业务成功（顶层 success 为布尔值 true）',
                                '响应无登录失效提示', '查看结果树', '汇总报告', '聚合报告'])
    def request = search.searchResults.first()
    def editor = new HttpTestSampleGui()
    editor.configure(request)
    def visit
    int edits = 0
    visit = { component ->
        if (component instanceof JTextComponent && component.text == '/guide?page=1') {
            component.text = '/guide?page=2'
            edits++
        }
        if (component instanceof Container) component.components.each { visit(it) }
    }
    visit(editor)
    assert edits == 1
    editor.modifyTestElement(request)
}
new File(args[2]).withOutputStream { SaveService.saveTree(plan, it) }
assert SaveService.loadTree(new File(args[2]))
System.exit(0)
