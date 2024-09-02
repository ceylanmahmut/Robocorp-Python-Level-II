from robocorp.tasks import task
from robocorp import browser
import requests
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
@task
def order_robot_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=200,headless=False)
    d_orders_file()
    open_order_website()
    fill_form_data()
    archive_receipts()

def d_orders_file():
    """Downloads the orders.csv file"""
    url = "https://robotsparebinindustries.com/orders.csv"
    response = requests.get(url, verify=False)
    with open("orders.csv", "wb") as file:
        file.write(response.content)

def open_order_website():
    """Opens the robot order website and clicks on OK"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click('text=OK')

def another_bot():
    """Clicks on 'Order another robot' button"""
    page = browser.page()
    page.click("#order-another")

def clicks_ok():
    """Clicks on 'OK' button"""
    page = browser.page()
    page.click('text=OK')

def fill_submit_data(order):
    """Fills in the robot order details and clicks the 'Order' button"""
    page = browser.page()
    head_names = {
        "1" : "Roll-a-thor head",
        "2" : "Peanut crusher head",
        "3" : "D.A.V.E head",
        "4" : "Andy Roid head",
        "5" : "Spanner mate head",
        "6" : "Drillbit 2000 head"
    }
    head_number = order["Head"]
    page.select_option("#head", head_names.get(head_number))
    page.click('//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{0}]/label'.format(order["Body"]))
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])
    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = receipt_as_pdf(int(order["Order number"]))
            screenshot_path = screenshot_robot(int(order["Order number"]))
            embed_screenshot_to_receipt(screenshot_path, pdf_path)
            another_bot()
            clicks_ok()
            break

def receipt_as_pdf(order_number):
    """Stores the order receipt as a PDF file"""
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path

def fill_form_data():
    """Fills the form with the data from the orders.csv file"""
    csv_file = Tables()
    robot_orders = csv_file.read_table_from_csv("orders.csv")
    for order in robot_orders:
        fill_submit_data(order)

def screenshot_robot(order_number):
    """Takes a screenshot of the ordered robot"""
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    """Embeds the screenshot to the receipt pdf"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot_path, source_path=pdf_path, output_path=pdf_path)
    
def archive_receipts():
    """Archives the receipts and the images"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")