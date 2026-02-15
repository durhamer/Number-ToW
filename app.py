import streamlit as st

# --- 1. 遊戲初始化 ---
if 'game_started' not in st.session_state:
    st.session_state.game_started = True
    st.session_state.rope_pos = 0
    st.session_state.p1_hand = [1, 2, 3, 4, 5, 0] # 0 代表空白
    st.session_state.p2_hand = [1, 2, 3, 4, 5, 0]
    st.session_state.current_turn = "CJ"
    st.session_state.p1_choice = None
    st.session_state.last_result = "遊戲開始！請 CJ 先出牌。"

# --- 2. 介面設定 ---
st.set_page_config(page_title="數字拔河博弈", layout="centered")
st.title("🪢 數字拔河：心理博弈版")

# 側邊欄顯示規則
with st.sidebar:
    st.header("遊戲規則")
    st.write("1. 雙方各有 1-5 加上一張**空白牌**。")
    st.write("2. **空白牌**：抵銷對方本輪所有出牌（對方白白浪費一張）。")
    st.write("3. 先將繩子拉到自己那一側 **±10** 或牌出完時領先者獲勝。")
    if st.button("重新開始遊戲"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 3. 視覺化繩子 ---
# 使用進度條模擬繩子，0 在中間 (50%)
# 範圍 -10 到 10 對應進度條 0% 到 100%
display_pos = (st.session_state.rope_pos + 10) / 20 
st.subheader(f"當前位置: {st.session_state.rope_pos}")
st.progress(display_pos)
col_left, col_mid, col_right = st.columns([1, 2, 1])
with col_left: st.write("⬅️ 兒子")
with col_right: st.write("CJ ➡️")

st.info(st.session_state.last_result)

# --- 4. 出牌邏輯 ---
def handle_move(card):
    if st.session_state.current_turn == "CJ":
        st.session_state.p1_choice = card
        st.session_state.p1_hand.remove(card)
        st.session_state.current_turn = "兒子"
        st.session_state.last_result = "CJ 已秘密出牌，換兒子出牌！"
    else:
        # 結算回合
        p1 = st.session_state.p1_choice
        p2 = card
        st.session_state.p2_hand.remove(card)
        
        if p1 == 0 or p2 == 0:
            res = f"結果：CJ 出 {p1 if p1!=0 else '空白'} | 兒子 出 {p2 if p2!=0 else '空白'}。空白牌發動，繩子不動！"
        else:
            diff = p1 - p2
            st.session_state.rope_pos += diff
            move_text = f"繩子向 {'CJ' if diff > 0 else '兒子'} 移動了 {abs(diff)} 格"
            res = f"結果：CJ 出 {p1} | 兒子 出 {p2}。{move_text}"
        
        st.session_state.last_result = res
        st.session_state.current_turn = "CJ"
        st.session_state.p1_choice = None

# --- 5. 按鈕介面 ---
if abs(st.session_state.rope_pos) >= 10 or (not st.session_state.p1_hand and not st.session_state.p1_choice):
    st.balloons()
    winner = "CJ" if st.session_state.rope_pos > 0 else "兒子"
    if st.session_state.rope_pos == 0: winner = "平局"
    st.success(f"🎊 遊戲結束！贏家是：{winner}")
else:
    st.write(f"### 現在輪到：{st.session_state.current_turn}")
    
    # 根據輪到誰顯示對應手牌
    current_hand = st.session_state.p1_hand if st.session_state.current_turn == "CJ" else st.session_state.p2_hand
    
    # 建立按鈕橫列
    cols = st.columns(len(current_hand))
    for i, card in enumerate(current_hand):
        label = "空白" if card == 0 else str(card)
        if cols[i].button(label, key=f"btn_{st.session_state.current_turn}_{card}"):
            handle_move(card)
            st.rerun()
