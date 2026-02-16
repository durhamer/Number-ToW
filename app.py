import streamlit as st

# --- 1. 穩健的初始化機制 ---
default_values = {
    'rope_pos': 0,
    'p1_hand': [1, 2, 3, 4, 5, 0],
    'p2_hand': [1, 2, 3, 4, 5, 0],
    'current_turn': "CJ",
    'p1_choice': None,
    'last_result': "遊戲開始！請 CJ 先出牌。",
    'phase': "play",
    'p2_visible_hand_for_cj': [1, 2, 3, 4, 5, 0], # CJ 視角看到的 JJ 手牌
    'p1_visible_hand_for_jj': [1, 2, 3, 4, 5, 0]  # JJ 視角看到的 CJ 手牌
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 2. 介面設定 ---
st.set_page_config(page_title="數字拔河博弈 - CJ vs JJ", layout="centered")
st.title("🪢 數字拔河：心理博弈版")

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
c_jj, c_mid, c_cj = st.columns([1, 2, 1])
c_jj.write("⬅️ 兒子 (JJ)")
c_cj.write("CJ ➡️")
st.divider()

# --- 4. 遊戲邏輯 ---

if st.session_state.phase == "confirm":
    st.warning("🔒 內容已隱藏，請將手機交給下一位玩家")
    if st.button(f"我是 {st.session_state.current_turn}，點擊開始出牌"):
        st.session_state.phase = "play"
        st.rerun()

else:
    st.info(st.session_state.last_result)
    
    is_game_over = abs(st.session_state.rope_pos) >= 10 or \
                  (not st.session_state.p1_hand and st.session_state.p1_choice is None)
    
    if is_game_over:
        winner = "CJ" if st.session_state.rope_pos > 0 else "兒子 (JJ)"
        if st.session_state.rope_pos == 0: winner = "平手"
        st.success(f"🎊 遊戲結束！贏家是：{winner}")
        st.balloons()
    else:
        # --- 核心邏輯修正：顯示「鎖定」的手牌資訊 ---
        if st.session_state.current_turn == "CJ":
            # CJ 看到的是 JJ 目前真正剩下的手牌
            opp_name = "兒子 (JJ)"
            display_hand = st.session_state.p2_hand
        else:
            # JJ 看到的是 CJ 出牌「之前」的手牌快照，這樣他才不知道 CJ 剛才出了什麼
            opp_name = "CJ"
            display_hand = st.session_state.p1_visible_hand_for_jj
        
        opp_hand_str = ", ".join(["空白" if c == 0 else str(c) for c in sorted(display_hand)])
        st.markdown(f"👀 **對手 ({opp_name}) 的剩餘手牌參考：** `{opp_hand_str}`")
        
        st.write(f"### 🫵 現在輪到：{st.session_state.current_turn}")
        
        current_hand = st.session_state.p1_hand if st.session_state.current_turn == "CJ" else st.session_state.p2_hand
        cols = st.columns(len(current_hand))
        
        for i, card in enumerate(current_hand):
            label = "空白" if card == 0 else str(card)
            if cols[i].button(label, key=f"btn_{st.session_state.current_turn}_{card}_{len(current_hand)}"):
                
                if st.session_state.current_turn == "CJ":
                    # 在 CJ 出牌前，先幫他記錄 JJ 目前的手牌快照 (雖然這步在單機版可選，但為了邏輯嚴謹保留)
                    # 關鍵：CJ 出牌後，我們不更新 p1_visible_hand_for_jj，直到這回合結束
                    st.session_state.p1_choice = card
                    st.session_state.p1_hand.remove(card)
                    st.session_state.current_turn = "兒子"
                    st.session_state.phase = "confirm"
                    st.session_state.last_result = "CJ 已秘密出牌！"
                else:
                    # JJ 出牌並結算
                    p1_v = st.session_state.p1_choice
                    p2_v = card
                    st.session_state.p2_hand.remove(card)
                    
                    if p1_v == 0 or p2_v == 0:
                        res = f"結果：CJ 出 {p1_v if p1_v!=0 else '空白'} | JJ 出 {p2_v if p2_v!=0 else '空白'}。空白牌發動，繩子不動！"
                    else:
                        diff = p1_v - p2_v
                        st.session_state.rope_pos += diff
                        res = f"結果：CJ 出 {p1_v} | JJ 出 {p2_v}。繩子移動了 {abs(diff)} 格！"
                    
                    # 回合結束，現在可以更新「可見手牌」快照了，供下一輪使用
                    st.session_state.p1_visible_hand_for_jj = list(st.session_state.p1_hand)
                    st.session_state.p2_visible_hand_for_cj = list(st.session_state.p2_hand)
                    
                    st.session_state.last_result = res
                    st.session_state.current_turn = "CJ"
                    st.session_state.p1_choice = None
                st.rerun()
