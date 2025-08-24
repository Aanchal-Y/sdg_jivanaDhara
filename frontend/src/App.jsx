import React from "react";
import Navbar from "./components/Navbar";
import Notifications from "./components/Notifications";
import { AppProvider } from "./context/AppContext";

function App() {
  return (
    <AppProvider>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <Notifications />
        {/* Add AIAdvisor, BlockchainWallet, CommunityForum here */}
      </div>
    </AppProvider>
  );
}

export default App;
