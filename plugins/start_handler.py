import sqlite3
from sqlite3 import Error
#from pyrogram.types.bots_and_keyboards import callback_query
from pyrogram.types.bots_and_keyboards.inline_keyboard_button import InlineKeyboardButton
from pyrogram.types.bots_and_keyboards.inline_keyboard_markup import InlineKeyboardMarkup
from pyromod import helpers
#from pyrogram.types.messages_and_media.message_entity import RAW_ENTITIES_TO_TYPE

from pyromod.helpers import ikb
from pyrogram import Client , filters
from pyrogram.types import Message
from pyrogram.types import CallbackQuery
from asyncio import TimeoutError
from plugins import admin






try:
        con = sqlite3.connect("fastfood_db.db")
        cur = con.cursor()
        
except Error as e:
        print(f"The bot is not able to connect to your database\n\n{Error}")

cur.execute("CREATE TABLE IF NOT EXISTS customer (id INTEGER PRIMARY KEY , firstname TEXT , lastname TEXT , address TEXT , phone_number TEXT)")
con.commit()

cur.execute("CREATE TABLE IF NOT EXISTS menu (name TEXT PRIMARY KEY, kind TEXT , price INTEGER)")
con.commit()

cur.execute("CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY , kind TEXT , name TEXT , number INTEGER , all_price INTEGER)")
con.commit()



#Inline Buttons 
start_btns_row1 = [("انتخاب غذا","set_order") , ("ثبت سفارش","send_order")]
start_btns_row2 = [("درباره ما","about_us") ,("ثبت اطلاعات","sign up")]
start_btns_row_admin = [("اضافه کردن","food_adding") ,("حذف غذا", "food_deleting")]
start_markup_customer = ikb([start_btns_row1 , start_btns_row2])
start_markup_admin = ikb([start_btns_row1 , start_btns_row2 , start_btns_row_admin])

def get_inline_btn_text(query):
    for item in query.message.reply_markup.inline_keyboard:
        #print(query)
        
        for member in item:
            #print(f"salam{query.data}")
            #print(member.callback_data)
            if query.data == member.callback_data:
                return member.text






@Client.on_message(filters.private & filters.command("start"))
async def start_section(c:Client , m:Message):
    from_user = m.from_user.id
   
    if(from_user == admin):
       
        await c.send_message(from_user , "برای ادامه  روی یکی از گزینه ها کلیک کنید اگر ثبت نام نکرده اید از قسمت ثبت اطلاعات استفاده کنید" , reply_markup= start_markup_admin)
    else :
        await c.send_message(from_user , "برای ادامه  روی یکی از گزینه ها کلیک کنید اگر ثبت نام نکرده اید از قسمت ثبت اطلاعات استفاده کنید" , reply_markup= start_markup_customer)
        
        
@Client.on_callback_query()        
async def sign_up(c:Client , m:CallbackQuery):
    from_user = m.from_user.id
    data = m.data

    is_admin = from_user == admin
    print(get_inline_btn_text(m))
    
    cur.execute(f"SELECT * FROM customer WHERE id = {from_user}")
    check_list = cur.fetchall()
    is_signedup = len(check_list)
    if data == "sign up":
        if is_signedup == 0:
            name = await c.ask(from_user , "لطفا نام کوچک خود را وارد کنید" , parse_mode= "Markdown")   
            last_name = await c.ask(from_user , f" عزیز لطفا نام خانوادگی خود را وارد کنید {name.text}" , parse_mode= "Markdown")
            address = await c.ask(from_user , f"ممنون از شما  عزیز آدرس خود جهت دریافت سفارشات را وارد کنید{name.text + last_name.text}" , parse_mode= "Markdown")
            phone_number = await c.ask(from_user , "شماره تلفن خود جهت هماهنگی با پیک وارد نمایید" , parse_mode= "Markdown")
            
            entity = (from_user , name.text , last_name.text , address.text , phone_number.text)
            
            cur.execute("INSERT INTO customer VALUES (?,?,?,?,?)" , entity)
            con.commit()
            
        elif is_signedup > 0:
            back_txt = "شما قبلا ثبت نام کرده اید "
            if is_admin == True:
                await m.edit_message_text( back_txt, reply_markup= start_markup_admin)
            else:
                await m.edit_message_text( back_txt, reply_markup= start_markup_customer)
        
    
        
    if data == "about_us" :
        about_text = "ما آدمای خوبی هستیم غذاهامونم خوشمزه هست"
        call_btn = ikb([[("شماره تماس","call_shop") , ("بازگشت","back")]])
        await m.edit_message_text(about_text , reply_markup= call_btn)
    
    if data == "call_shop":
        back_btn_1 = ikb([[("بازگشت" , "back_to_page1_data")]])
        await c.send_message(from_user , "زنگ بزن 118" , reply_markup= back_btn_1)
        
        
    if(data == "back"):
        text = "برای ادامه  روی یکی از گزینه ها کلیک کنید اگر ثبت نام نکرده اید از قسمت ثبت اطلاعات استفاده کنید"
        if is_admin == True:
            await m.edit_message_text(text , reply_markup= start_markup_admin)
        else:
            await m.edit_message_text(text , reply_markup= start_markup_customer)
            
    #str_menu_groups = []     
    cur.execute("SELECT kind FROM menu ")
    group_food_list = cur.fetchall()    
    group_list = []
    for item in group_food_list:
        if not item in group_list:
            group_list.append(item)
            
    

        
    if(data == "food_adding" and is_admin == True):
        keyboards = []
        members = []
        helper_list = []
        for item in group_list:
            members.append((item[0],f"add-{item[0]}"))
            if len(members) == 2:
                helper_list.append(members) 
                keyboards.extend(helper_list)
                members = []
                helper_list = []
                
                
                
        if len(members) < 2:
            members.append(("گروه دیگر" , "other"))
            helper_list.append(members)
            keyboards.extend(helper_list)
            
        
        #print(f"len_members = {len(members)}  members = {members}    keyboards = {keyboards} \nhelper_list = {helper_list}")
        
        #print([[btn for btn in row] for row in keyboards])
        
        
        add_buttons = ikb([[btn for btn in row] for row in keyboards])
        text_add = "برای ادامه کار یکی از گروه های غذایی زیر را انتخاب کنید"
        await m.edit_message_text(text = text_add , reply_markup= add_buttons)
        
    if(data.startswith("add") and is_admin == True):
        
        text = "نام غذای خود را وارد کنید"
        food_name = await c.ask(from_user , text , parse_mode= "Markdown")
        
        btn_text = get_inline_btn_text(m)
        print(f"SALAM {btn_text}")
        
        
        text_price = "قیمت غذا را وارد کنید"
        price_of_food = await c.ask(from_user , text_price , parse_mode= "Markdown") 
        #print(f"priceOfFOOD === {price_of_food} \n price_txt === {price_of_food.text}")
        while type(price_of_food) != type(5):
            try:
                price_of_food = int(price_of_food.text)
            except:
                price_of_food = await c.ask(from_user , "خطا »»» لطفا یک عدد به لاتین وارد کنید", parse_mode= "Markdown")
                  

        cur.execute("INSERT INTO menu VALUES (?,?,?)" , (food_name.text,btn_text,price_of_food))
        con.commit()
        back_to_page1_btn = ikb([[("بازگشت به صفحه اول" , "back_to_page1_data")] , [("افزودن غذای دیگر" , "food_adding")]])
        text1 = f"غذای مورد نظر با نام {food_name.text} در گروه {btn_text} ذخیره شد"
        await c.send_message(from_user , text1 , reply_markup= back_to_page1_btn)
        
    elif(data == "other" and is_admin == True):
        text_group = "گروه غذایی مورد نظر را وارد کنید"
        group_text = await c.ask(from_user , text_group , parse_mode= "Markdown")   
        text_name = "نام غذا را وارد کنید"
        name_text = await c.ask(from_user , text_name , parse_mode= "Markdown") 

        text_price = "قیمت غذا را وارد کنید"
        price_of_food = await c.ask(from_user , text_price , parse_mode= "Markdown") 
        
        while type(price_of_food) != type(5):
            try:
                price_of_food = int(price_of_food.text)
            except:
                price_of_food = await c.ask(from_user , "خطا »»» لطفا یک عدد به لاتین وارد کنید", parse_mode= "Markdown")
                  

        cur.execute("INSERT INTO menu VALUES (?,?,?)" , (name_text.text,group_text.text,price_of_food))
        con.commit()
        
        
        back_to_page1_btn = ikb([[("بازگشت به صفحه اول" , "back_to_page1_data")] , [("افزودن غذای دیگر" , "food_adding")]])
        await c.send_message(from_user , f"غذای مورد نظر شما با نام {name_text.text} در گروه {group_text.text} ذخیره شد." , reply_markup= back_to_page1_btn)
        
    
       
    if(data == "food_deleting" and is_admin == True):
        
        keys = ikb([[("کل گروه غذایی" , "to_delete_group_all") , ("یک غذای خاص" , "just_one")],[("بازگشت به صفحه اول" , "back_to_page1_data")]])
        text_ask = "مایل به حذف یک گروه هستید یا یک غذای خاص؟"
        await m.edit_message_text(text = text_ask , reply_markup= keys)
        
    
    
    
    if(data == "to_delete_group_all"):
        
        keyboards = []
        members = []
        helper_list = []
        for item in group_list:
            members.append((item[0],f"clear-{item[0]}"))
            if len(members) == 2:
                helper_list.append(members) 
                keyboards.extend(helper_list)
                members = []
                helper_list = []
        if len(members) == 1:       
            helper_list.append(members)
            keyboards.extend(helper_list)
        #back_list = [("انصراف" , "back_to_page1_data")]
        #keyboards.append(back_list)    
        del_buttons = ikb([[btn for btn in row] for row in keyboards])
        
        delete_text = "برای حذف غذا یکی از گروه های غذایی زیر را انتخاب کنید"
        await m.edit_message_text(delete_text , reply_markup= del_buttons)
  
  
    
    
    if data.startswith("clear"):
        group_name_to_delete = get_inline_btn_text(m)
        
        
        
        cur.execute("DELETE FROM menu WHERE kind = ? " , (group_name_to_delete , ) )
        con.commit()
        txtOfDEL = f"گروه غذایی با نام {group_name_to_delete} به طور کامل حذف گردید"
        await c.send_message(from_user , txtOfDEL)
                        
    if(data == "just_one"):
        
        keyboards = []
        members = []
        helper_list = []
        for item in group_list:
            members.append((item[0],f"del-{item[0]}"))
            if len(members) == 2:
                helper_list.append(members) 
                keyboards.extend(helper_list)
                members = []
                helper_list = []
                
        helper_list.append(members)
        keyboards.extend(helper_list)
        back_list = [("انصراف" , "back_to_page1_data")]
        keyboards.append(back_list)    
        del_buttons = ikb([[btn for btn in row] for row in keyboards])
        delete_text = "برای حذف غذا گروه غذایی آن را انتخاب کنید"
        await m.edit_message_text(text = delete_text , reply_markup= del_buttons)
        
       
    if data.startswith("del"):
        btn_txt = get_inline_btn_text(m)
        
        cur.execute("SELECT name FROM menu WHERE kind = ?" , (btn_txt , ))
        name_list_of_group_to_delete = cur.fetchall()
        names_of_one_group = []
        
        for item in name_list_of_group_to_delete:
            item = item[0]
            names_of_one_group.append(item)
        
        keys = []
        members = []
        btns = []
        for item in names_of_one_group:
            members = []
            members.append((item , f"onedel-{item}"))
            if len(members) == 2:
                keys.extend(members)
                
            if len(members) == 1:
                keys.extend(members)
                
                
        btns.append(keys)        
        back_list = [("انصراف" , "back_to_page1_data")]
        btns.append(back_list)        
        del_name_buttons = ikb([[btn for btn in row] for row in btns])
        text_choice_del = "نام غذا را انتخاب کنید"
        await m.edit_message_text(text_choice_del , reply_markup= del_name_buttons)
        
        
        
    if data.startswith("onedel"):
        food_name_del = get_inline_btn_text(m)
        
        #cur.execute(f"SELECT kind FROM menu WHERE name == {food_name_del}")
        #group = cur.fetchone()
        
        cur.execute("DELETE FROM menu WHERE name = ?" ,(food_name_del , ))
        con.commit()
        back_btn = ikb([[("بازگشت" , "back_to_page1_data")]])   
        await m.edit_message_text(text= f"غذای مورد نظر با نام {food_name_del} حذف شد" , reply_markup= back_btn)
            
 
            
            
    #str_menu_groups_for_order = []  
    #str_menu_names_for_order = []
          
    if( data == "set_order"):    #  انتخاب غذا
        keyboards = []
        members = []
        helper_list = []
        for item in group_list:
            members.append((item[0],f"choice-{item[0]}"))
            if len(members) == 2:
                helper_list.append(members) 
                keyboards.extend(helper_list)
                members = []
                helper_list = []
        if len(members) == 1:       
            helper_list.append(members)
            keyboards.extend(helper_list)
        back_list = [("انصراف" , "back_to_page1_data")]
        keyboards.append(back_list)    
        set_buttons = ikb([[btn for btn in row] for row in keyboards])
        set_text = "برای انتخاب غذا یکی از گروه های غذایی زیر را انتخاب کنید"
        await m.edit_message_text(set_text , reply_markup= set_buttons)
        
        #print(f"aaa »»» {set_btn_text.text}")
        '''txt_of_groups = []
        for item in group_list:
            print(item[0])
            txt_of_groups.append(item[0])'''
    
            
    if data.startswith("choice"):
        txtOfBtn = get_inline_btn_text(m)
        #await c.send_message(from_user , txtOfBtn)
        cur.execute("SELECT name FROM menu WHERE kind= ?",(txtOfBtn , ))
        name_list_of_this_group = cur.fetchall()
        keyboards = []
        members = []
        helper_list = []
           
        for item in name_list_of_this_group:
            members.append((item[0],f"order-{item[0]}"))
            if len(members) == 2:
                helper_list.append(members) 
                keyboards.extend(helper_list)
                members = []
                helper_list = []
                
        if len(members) == 1:       
          helper_list.append(members)
          keyboards.extend(helper_list)   
        back_list = [("انصراف" , "back_to_page1_data")]
        keyboards.append(back_list)        
        set_buttons = ikb([[btn for btn in row] for row in keyboards])
        order_txt = "غذای مورد نظر را انتخاب کنید"
        await m.edit_message_text(order_txt , reply_markup= set_buttons)
        

    if data.startswith("order"):
        order_name = get_inline_btn_text(m)
        #cur.execute(f"SELECT name FROM menu WHERE kind =:kind", {'kind': str_food})
        cur.execute("SELECT kind FROM menu WHERE name = ?" , (order_name , ))
        order_kind = cur.fetchone()
        
        number_of_order = await c.ask(from_user , f"چند تا {order_name} نیاز دارید؟؟", parse_mode= "Markdown")
        
        while type(number_of_order) != type(5):
            try:
                number_of_order = int(number_of_order.text)
            except:
                number_of_order = await c.ask(from_user , "لطفا یک عدد به لاتین وارد کنید", parse_mode= "Markdown")
        
        
      
        cur.execute("SELECT price FROM menu WHERE name = ?" , (order_name , ))
        order_cost = cur.fetchone()
        
        price_of_order = number_of_order * order_cost[0]
                  
        cur.execute("INSERT INTO orders VALUES(?,?,?,?,?)" , [from_user , order_kind[0] , order_name , number_of_order , price_of_order])
        con.commit()
        
        
        
        set_finall_btns = ikb([[("   سفارش مورد بعدی   " , "set_order") , ("بازگشت به صفحه اول برای ثبت" , "back_to_page1_data")]])
        await c.send_message(from_user , "سفارش شما ثبت شد"  , reply_markup= set_finall_btns)
            
    if data == "back_to_page1_data":
        if(from_user == admin):
            await c.send_message(from_user , "برای ویرایش،ثبت و پرداخت هزینه سفارش گزینه ثبت سفارش را کلیک کنید" , reply_markup= start_markup_admin)
        else :
            await c.send_message(from_user , "برای ویرایش،ثبت و پرداخت هزینه سفارش گزینه ثبت سفارش را کلیک کنید" , reply_markup= start_markup_customer)
                    
            
            
                
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            

    
    
    if data == "send_order":
        #print(orders_list)
        cur.execute(f"SELECT * FROM orders WHERE id == {from_user}")
        orders_list = cur.fetchall()
        
        text = "سفارش شما عبارت است از :\n"
        index = 0
        all_price_orders = 0
        
        for list in orders_list:
            index += 1
            text += f"{index} === {list[1]} , {list[2]} , {list[3]}تا , {list[4]} \n\n"
            all_price_orders += list[4]
        
        text += f"\n\nهزینه کل سفارشات برابر است با{all_price_orders}"    
        send_btns = ikb([ [("ارسال سفارش" , "send_it") , ("ویرایش" , "edit")] , [("انصراف" , "back_to_page1_data")] ])
        
        
        await m.edit_message_text(text = text , reply_markup= send_btns)
       
        
    
    if(data == "edit"):
        
        cur.execute(f"SELECT * FROM orders WHERE id = ? " , (from_user , ))
        orders_list = cur.fetchall()
        
        edit_list = []
        
        #counter = 0
        for list in orders_list:
            #counter += 1
            edit_list.append((list[1] , f"const_{list[1]}"))
        
        edit_btns = ikb( [ [edit_button for edit_button in edit_list] ] )
        await c.send_message(from_user ,text = "برای ویرایش گزینه مورد نظر را انتخاب کنید" , reply_markup= edit_btns)
        
    if(data.startswith("const")):
        
        const_txt = get_inline_btn_text(m)
           
        cur.execute("DELETE FROM orders WHERE id = ? AND kind = ? " , (from_user , const_txt) )
        con.commit()
        
        txt = "سفارش انتخاب شده  با موفقیت حذف شد \nبرای سفارش مجدد یا ثبت و پرداخت از گزینه های زیر استفاده کنید"
        edit_btns_2 = ikb([[("ویرایش مجدد" , "edit") , ("ارسال باقیمانده سفارش" , "send_it")]])
        await m.edit_message_text(text = txt , reply_markup= edit_btns_2)
        
        
    if(data == "send_it"):
        
        send_way_btns = ikb ([[("ارسال با پیک" , "ersal_delivery") , ("تحویل حضوری" , "themselves")]])
        await m.edit_message_text(text = "نحوه دریافت غذا را انتخاب کنید\nهزینه ارسال با پیک 10000 تومان" , reply_markup= send_way_btns)
        
    if data == "ersal_delivery":
        cur.execute("SELECT price FROM orders WHERE id = ? " , (from_user , ))
        price_all_orders_delivery = cur.fetchall()
        all_price = 0
        for item in price_all_orders_delivery:
            all_price += item[0]
        
        finall_payment = all_price + 10000
        text_pay = f"مبلغ قابل پرداخت برابر است با   {finall_payment}  تومان"
        pay_btn = ikb([[("رفتن به درگاه پرداخت" , "pay") , ("بازگشت به صفحه اول" , "back_to_page1_data")]])
        await m.edit_message_text(text = text_pay , reply_markup= pay_btn)
        
    if data == "themselves":
        cur.execute("SELECT all_price FROM orders WHERE id = ? " , (from_user , ))
        price_all_orders_delivery = cur.fetchall()
        all_price = 0
        for item in price_all_orders_delivery:
            all_price += item[0]
        
        finall_payment = all_price
        text_pay = f"مبلغ قابل پرداخت برابر است با   {finall_payment}  تومان"
        pay_btn = ikb([[("رفتن به درگاه پرداخت" , "pay") , ("بازگشت به صفحه اول" , "backtopage1")]])
        await m.edit_message_text(text = text_pay , reply_markup= pay_btn)
        
        
    if(data == "pay"):
        await m.edit_message_text("پرداخت شما انجام شد منتظر سفارش بمانید")
    
    '''if(data == "backtopage1"):
        
        if(from_user == admin):
            await m.edit_message_text(text = "برای ادامه  روی یکی از گزینه ها کلیک کنید اگر ثبت نام نکرده اید از قسمت ثبت اطلاعات استفاده کنید" , reply_markup= start_markup_admin)
        else:
            await m.edit_message_text(text = "برای ادامه  روی یکی از گزینه ها کلیک کنید اگر ثبت نام نکرده اید از قسمت ثبت اطلاعات استفاده کنید" , reply_markup= start_markup_customer)
        
    '''
    
    