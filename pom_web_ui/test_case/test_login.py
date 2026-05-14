import time
from common.base_page import DriverFactory
from navigation.navigator import Navigator
from pages.registry.page_registry import PageRegistry


class TestLogin(object):

    def test1(self):
        driver = DriverFactory.get_driver()
        driver.maximize_window()

        navigator = Navigator(driver)
        registry = PageRegistry(driver)

        page_id = navigator.goto_login()  # 进入页面，获取页面ID
        registry.get(page_id)  # 获取登录类的实例对象

        registry.LoginPage.login()

        for i in range(10):
            # 进入数字阅片
            navigator.goto_module_digital_reading()
            p_id = navigator.goto_project_list()
            registry.get(p_id)

            registry.ProjectListPage.goto_tab_all()
            row_el = registry.ProjectListPage.get_bone_first_row()
            registry.ProjectListPage.open(row_el)

            p_id = navigator.goto_project_detail()
            registry.get(p_id)
            registry.ProjectDetailPage.switch_report_editor()

            p_id = navigator.goto_report_editor()
            registry.get(p_id)

            closed_dialog = registry.ReportEditorPage.open_permanently_closed_dialog()
            result = closed_dialog.permanently_closed()
            assert result
            synchronization_dialog = registry.ReportEditorPage.open_synchronization_dialog()
            synchronization_dialog.synchronization()

            registry.ReportEditorPage.input_bone_analysis("""1.骨髓小粒丰富，取材、制片、染色佳。
        2.骨髓有核细胞增生极度活跃，粒红比=1.37:1。
        3.粒系增生活跃，占49.5%，以中性晚幼粒及以下细胞增生为主，可见细胞巨幼变，巨晚幼粒细胞、巨杆状核粒细胞易见。
        4.红系增生活跃，占36.0%，以中、晚幼红细胞增生为主，幼红细胞巨幼变明显，成熟红细胞大小不均，巨红细胞易见。
        5.单核细胞占1.0%，淋巴细胞占12.5%，浆细胞占0.7%，均为成熟细胞。
        6.巨核细胞全片计数0个，分类25个，其中产血小板型巨核细胞0个，血小板小簇可见。""")
            registry.ReportEditorPage.input_blood_analysis("""提示巨幼细胞性贫血骨髓象，请结合叶酸、VB12检查""")
            registry.ReportEditorPage.input_opinion("""提示巨幼细胞性贫血骨髓象，请结合叶酸、VB12检查""")

            registry.ReportEditorPage.select_examining_doctor('shi')
            registry.ReportEditorPage.select_reviewing_doctor('shi2')

            registry.ReportEditorPage.select_reviewing_time('2030-12-12')
            registry.ReportEditorPage.select_reporting_time('2019-12-12')

            registry.ReportEditorPage.upload_picture('C:\\Users\\shi\\Desktop\\图片\\小程序-桌面.png')

            registry.ReportEditorPage.save_report()
            # toast.wait_toast_and_disappear('保存成功')
            submit_dialog = registry.ReportEditorPage.open_submit_dialog()
            submit_dialog.confirm()

            registry.ReportEditorPage.toast_submission_success()
            time.sleep(1)
