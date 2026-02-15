import streamlit as st

# --- 1. 遊戲初始化 ---
if 'game_started' not in st.session_state:
    st.session_state.rope_pos = 0
    st.session_state.p1_hand = [1, 2, 3, 4, 5, 0]
    st.session_state.p2_hand = [1, 2, 3, 4, 5, 0]
    st.session_state.current_turn = "CJ"
    st.session_state.p1_choice = None
    st.session_state.last_result = "遊戲開始！請 CJ 先出牌。"
    # 新增 phase: "play" (出牌中) 或 "confirm" (換人確認中)
    st.session_state.phase = "play" 

st.set_page_config(page_title="數字拔河博弈", layout="centered")
st.title("🪢 數字拔河：心理博弈版")

# 側邊欄重置按鈕
if st.sidebar.button("重新開始遊戲"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- 2. 視覺化繩子 ---
display_pos = (st.session_state.rope_pos + 10) / 20 
st.subheader(f"當前位置: {st.session_state.rope_pos}")
st.progress(display_pos)
c1, c2, c3 = st.columns([1, 2, 1])
c1.write("⬅️ 兒子 (JJ)")
c3.write("CJ ➡️")

# --- 3. 遊戲邏輯與畫面切換 ---

# 階段 A：換人確認畫面 (避免洩漏答案)
if st.session_state.phase == "confirm":
    st.warning("⚠️ 請將手機交給下一位玩家")
    if st.button(f"我是 {st.session_state.current_turn}，我準備好了"):
        st.session_state.phase = "play"
        st.rerun()

# 階段 B：出牌畫面
else:
    st.info(st.session_state.last_result)
    
    # 檢查勝負
    if abs(st.session_state.rope_pos) >= 10 or (not st.session_state.p1_hand and st.session_state.p1_choice is None):
        winner = "CJ" if st.session_state.rope_pos > 0 else "兒子 (JJ)"
        if st.session_state.rope_pos == 0: winner = "平局"
        st.success(f"🎊 遊戲結束！贏家是：{winner}")
        st.balloons()
    else:
        st.write(f"### 現在輪到：{st.session_state.current_turn}")
        
        current_hand = st.session_state.p1_hand if st.session_state.current_turn == "CJ" else st.session_state.p2_hand
        
        # 使用 columns 讓按鈕橫排，減少誤觸也比較美觀
        cols = st.columns(len(current_hand))
        for i, card in enumerate(current_hand):
            label = "空白" if card == 0 else str(card)
            # 使用唯一 key 確保 Streamlit 重新渲染時不會殘留狀態
            if cols[i].button(label, key=f"btn_{st.session_state.current_turn}_{card}_{len(current_hand)}"):
                if st.session_state.current_turn == "CJ":
                    st.session_state.p1_choice = card
                    st.session_state.p1_hand.remove(card)
                    st.session_state.current_turn = "兒子"
                    st.session_state.phase = "confirm" # 進入確認畫面
                    st.session_state.last_result = "CJ 已出牌，換兒子 (JJ)！"
                else:
                    # 結算
                    p1 = st.session_state.p1_choice
                    p2 = card
                    st.session_state.p2_hand.remove(card)
                    if p1 == 0 or p2 == 0:
                        res = f"結果：CJ 出 {p1 if p1!=0 else '空白'} | JJ 出 {p2 if p2!=0 else '空白'}。空白牌發動，繩子不動！"
                    else:
                        diff = p1 - p2
                        st.session_state.rope_pos += diff
                        res = f"結果：CJ 出 {p1} | JJ 出 {p2}。繩子移動了 {abs(diff)} 格！"
                    
                    st.session_state.last_result = res
                    st.session_state.current_turn = "CJ"
                    st.session_state.p1_choice = None
                    # 結算後也可以加一個確認，看你想不想讓下一輪開始前也遮蔽
                    # st.session_state.phase = "confirm" 
                st.rerun()
