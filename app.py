import streamlit as st

# --- 1. 穩健的初始化機制 ---
# 使用 default_values 確保所有變數在任何時候都能被正確存取
default_values = {
    'rope_pos': 0,
    'p1_hand': [1, 2, 3, 4, 5, 0],
    'p2_hand': [1, 2, 3, 4, 5, 0],
    'current_turn': "CJ",
    'p1_choice': None,
    'last_result': "遊戲開始！請 CJ 先從手牌中選擇一張。",
    'phase': "play"  # 分為 "play" 出牌階段 與 "confirm" 換人遮蔽階段
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
    st.write("2. **空白牌**：讓對手該輪無效（白白浪費一張牌）。")
    st.write("3. 先拉到 **±10** 或牌出完時領先者勝。")
    if st.button("🔄 重新開始遊戲"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- 3. 視覺化繩子 ---
# 將 -10 到 10 映射到進度條的 0.0 到 1.0
display_pos = (st.session_state.rope_pos + 10) / 20 
st.subheader(f"目前繩子位置: {st.session_state.rope_pos}")
st.progress(display_pos)

col_jj, col_center, col_cj = st.columns([1, 2, 1])
col_jj.write("⬅️ 兒子 (JJ)")
col_cj.write("CJ ➡️")

st.divider()

# --- 4. 遊戲邏輯與流程控制 ---

# 階段 A：換人遮蔽畫面 (解決洩漏答案問題)
if st.session_state.phase == "confirm":
    st.warning("🔒 內容已隱藏，請將手機交給下一位玩家")
    if st.button(f"我是 {st.session_state.current_turn}，點擊開始出牌"):
        st.session_state.phase = "play"
        st.rerun()

# 階段 B：正式出牌畫面
else:
    st.info(st.session_state.last_result)
    
    # 勝負判定：繩子達標或手牌用盡
    is_game_over = abs(st.session_state.rope_pos) >= 10 or \
                  (not st.session_state.p1_hand and st.session_state.p1_choice is None)
    
    if is_game_over:
        winner = "CJ" if st.session_state.rope_pos > 0 else "兒子 (JJ)"
        if st.session_state.rope_pos == 0: winner = "平手"
        st.success(f"🎉 遊戲結束！贏家是：{winner}")
        st.balloons()
    else:
        st.write(f"### 🫵 現在輪到：{st.session_state.current_turn}")
        
        # 取得當前玩家手牌
        current_hand = st.session_state.p1_hand if st.session_state.current_turn == "CJ" else st.session_state.p2_hand
        
        # 顯示手牌按鈕 (加上 len 確保 key 唯一，避免反白殘留)
        cols = st.columns(len(current_hand))
        for i, card in enumerate(current_hand):
            label = "空白" if card == 0 else str(card)
            if cols[i].button(label, key=f"btn_{st.session_state.current_turn}_{card}_{len(current_hand)}"):
                
                if st.session_state.current_turn == "CJ":
                    # CJ 出牌邏輯
                    st.session_state.p1_choice = card
                    st.session_state.p1_hand.remove(card)
                    st.session_state.current_turn = "兒子"
                    st.session_state.phase = "confirm"  # 進入遮蔽畫面
                    st.session_state.last_result = "CJ 已秘密出牌！"
                else:
                    # JJ 出牌並結算
                    p1_val = st.session_state.p1_choice
                    p2_val = card
                    st.session_state.p2_hand.remove(card)
                    
                    if p1_val == 0 or p2_val == 0:
                        res = f"結果：CJ 出 {p1_val if p1_val!=0 else '空白'} | JJ 出 {p2_val if p2_val!=0 else '空白'}。空白牌發動，雙方平手！"
                    else:
                        diff = p1_val - p2_val
                        st.session_state.rope_pos += diff
                        res = f"結果：CJ 出 {p1_val} | JJ 出 {p2_val}。繩子向 {'CJ' if diff > 0 else 'JJ'} 移動了 {abs(diff)} 格！"
                    
                    st.session_state.last_result = res
                    st.session_state.current_turn = "CJ"
                    st.session_state.p1_choice = None
                    # 結算後是否要遮蔽可依個人喜好，這裡設定直接回 CJ 畫面
                st.rerun()
