import streamlit as st

# --- 1. 穩健的初始化機制 ---
default_values = {
    'rope_pos': 0,
    'p1_hand': [1, 2, 3, 4, 5, 0],
    'p2_hand': [1, 2, 3, 4, 5, 0],
    'current_turn': "CJ",
    'p1_choice': None,
    'last_result': "遊戲開始！請 CJ 先出牌。",
    'phase': "play" 
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 2. 介面設定 ---
st.set_page_config(page_title="數字拔河博弈 - CJ vs JJ", layout="centered")
st.title("🪢 數字拔河：心理博弈版")

# 側邊欄：規則與重置
with st.sidebar:
    st.header("遊戲說明")
    st.write("1. 雙方各有 1-5 與一張 **空白牌**。")
    st.write("2. **空白牌**：抵銷對方本輪出牌。")
    if st.button("🔄 重新開始遊戲"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 3. 視覺化繩子 ---
display_pos = (st.session_state.rope_pos + 10) / 20 
st.subheader(f"目前繩子位置: {st.session_state.rope_pos}")
st.progress(display_pos)

col_jj, col_center, col_cj = st.columns([1, 2, 1])
col_jj.write("⬅️ 兒子 (JJ)")
col_cj.write("CJ ➡️")

st.divider()

# --- 4. 遊戲邏輯與流程控制 ---

# 階段 A：換人遮蔽畫面
if st.session_state.phase == "confirm":
    st.warning("🔒 內容已隱藏，請將手機交給下一位玩家")
    if st.button(f"我是 {st.session_state.current_turn}，點擊開始出牌"):
        st.session_state.phase = "play"
        st.rerun()

# 階段 B：正式出牌畫面
else:
    st.info(st.session_state.last_result)
    
    # 勝負判定
    is_game_over = abs(st.session_state.rope_pos) >= 10 or \
                  (not st.session_state.p1_hand and st.session_state.p1_choice is None)
    
    if is_game_over:
        winner = "CJ" if st.session_state.rope_pos > 0 else "兒子 (JJ)"
        if st.session_state.rope_pos == 0: winner = "平手"
        st.success(f"🎊 遊戲結束！贏家是：{winner}")
        st.balloons()
    else:
        # 顯示對手手牌 (新功能)
        opponent_name = "兒子 (JJ)" if st.session_state.current_turn == "CJ" else "CJ"
        opponent_hand = st.session_state.p2_hand if st.session_state.current_turn == "CJ" else st.session_state.p1_hand
        
        # 格式化顯示手牌，0 顯示為 "空白"
        opp_hand_str = ", ".join(["空白" if c == 0 else str(c) for c in sorted(opponent_hand)])
        st.markdown(f"👀 **對手 ({opponent_name}) 的剩餘手牌：** `{opp_hand_str}`")
        
        st.write(f"### 🫵 現在輪到：{st.session_state.current_turn}")
        
        # 取得當前玩家手牌
        current_hand = st.session_state.p1_hand if st.session_state.current_turn == "CJ" else st.session_state.p2_hand
        
        cols = st.columns(len(current_hand))
        for i, card in enumerate(current_hand):
            label = "空白" if card == 0 else str(card)
            if cols[i].button(label, key=f"btn_{st.session_state.current_turn}_{card}_{len(current_hand)}"):
                
                if st.session_state.current_turn == "CJ":
                    st.session_state.p1_choice = card
                    st.session_state.p1_hand.remove(card)
                    st.session_state.current_turn = "兒子"
                    st.session_state.phase = "confirm"
                    st.session_state.last_result = "CJ 已秘密出牌！"
                else:
                    p1_val = st.session_state.p1_choice
                    p2_val = card
                    st.session_state.p2_hand.remove(card)
                    
                    if p1_val == 0 or p2_val == 0:
                        res = f"結果：CJ 出 {p1_val if p1_val!=0 else '空白'} | JJ 出 {p2_val if p2_val!=0 else '空白'}。空白牌發動，繩子不動！"
                    else:
                        diff = p1_val - p2_val
                        st.session_state.rope_pos += diff
                        res = f"結果：CJ 出 {p1_val} | JJ 出 {p2_val}。繩子移動了 {abs(diff)} 格！"
                    
                    st.session_state.last_result = res
                    st.session_state.current_turn = "CJ"
                    st.session_state.p1_choice = None
                st.rerun()
