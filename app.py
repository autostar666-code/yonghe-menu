import streamlit as st
from dataclasses import dataclass, field
from typing import List

# --- 1. 資料結構 (跟剛剛一樣，沒變) ---
@dataclass
class Modifier:
    id: str
    name: str
    price_delta: int = 0

@dataclass
class MenuItem:
    id: str
    category: str
    name: str
    price: int
    allowed_modifiers: List[str] = field(default_factory=list)

@dataclass
class OrderItem:
    item: MenuItem
    modifiers: List[Modifier] = field(default_factory=list)
    quantity: int = 1
    
    @property
    def subtotal(self):
        return (self.item.price + sum(m.price_delta for m in self.modifiers)) * self.quantity

# --- 2. 資料庫設定 (跟剛剛一樣) ---
mods_db = {
    "sugar_full": Modifier("sugar_full", "全糖", 0),
    "sugar_half": Modifier("sugar_half", "半糖", 0),
    "sugar_no":   Modifier("sugar_no", "無糖", 0),
    "temp_ice":   Modifier("temp_ice", "冰", 0),
    "temp_hot":   Modifier("temp_hot", "熱", 0),
    "add_egg":    Modifier("add_egg", "加蛋", 15),
    "add_cheese": Modifier("add_cheese", "加起司", 15),
}

menu_db = [
    MenuItem("d01", "DRINKS", "非基改豆漿", 25, ["sugar_full", "sugar_half", "sugar_no", "temp_ice", "temp_hot"]),
    MenuItem("c01", "ROLLS", "經典燒餅油條", 40),
    MenuItem("e01", "CREPES", "原味Q蛋餅", 30, ["add_cheese"]),
    MenuItem("t01", "EATS", "招牌飯糰", 40, ["add_egg"]),
]

# --- 3. Streamlit 網頁介面設計 ---

st.title("🏠 永和日常 - 線上點餐")
st.write("每日現磨・手工製作 | EST. TAIWANESE BREAKFAST")

# 初始化購物車 (session_state 是網頁暫存記憶體)
if 'cart' not in st.session_state:
    st.session_state.cart = []

# --- 側邊欄：點餐區 ---
with st.sidebar:
    st.header("🛒 開始點餐")
    
    # 1. 選擇餐點
    item_names = [item.name for item in menu_db]
    selected_name = st.selectbox("請選擇餐點", item_names)
    
    # 找到對應的物件
    selected_item = next(item for item in menu_db if item.name == selected_name)
    
    st.metric("單價", f"${selected_item.price}")

    # 2. 選擇客製化選項 (如果有)
    selected_mods = []
    if selected_item.allowed_modifiers:
        st.subheader("客製化選項")
        for mod_id in selected_item.allowed_modifiers:
            mod = mods_db.get(mod_id)
            if mod:
                # 使用 checkbox 讓客人勾選
                if st.checkbox(f"{mod.name} (+${mod.price_delta})", key=mod_id):
                    selected_mods.append(mod)

    # 3. 選擇數量
    qty = st.number_input("數量", min_value=1, value=1)

    # 4. 加入購物車按鈕
    if st.button("➕ 加入清單"):
        order_item = OrderItem(item=selected_item, modifiers=selected_mods, quantity=qty)
        st.session_state.cart.append(order_item)
        st.success(f"已加入：{selected_item.name}")

# --- 主畫面：顯示訂單 ---
st.subheader("🧾 您的訂單明細")

if not st.session_state.cart:
    st.info("購物車目前是空的，請由左側點餐。")
else:
    total_amount = 0
    
    # 顯示表格
    for i, order in enumerate(st.session_state.cart):
        mod_text = f"({', '.join([m.name for m in order.modifiers])})" if order.modifiers else ""
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{order.item.name}** {mod_text}")
        with col2:
            st.write(f"x{order.quantity}")
        with col3:
            st.write(f"${order.subtotal}")
        
        total_amount += order.subtotal

    st.markdown("---")
    st.title(f"💰 總金額: ${total_amount}")
    
    if st.button("✅ 送出訂單 (模擬)"):
        st.balloons() # 放煙火特效
        st.success("訂單已送出！廚房準備中...")
        # 這裡未來可以串接 LINE Notify 通知老闆