import React, { createContext, useReducer, useContext } from "react";

const AppContext = createContext();

const initialState = {
  user: null,
  token: null,
  sdgData: {},
  notifications: []
};

function reducer(state, action) {
  switch (action.type) {
    case "LOGIN":
      return { ...state, user: action.payload.user, token: action.payload.token };
    case "LOGOUT":
      return { ...state, user: null, token: null };
    case "ADD_NOTIFICATION":
      return { ...state, notifications: [...state.notifications, action.payload] };
    default:
      return state;
  }
}

export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  return <AppContext.Provider value={{ state, dispatch }}>{children}</AppContext.Provider>;
};

export const useAppContext = () => useContext(AppContext);
