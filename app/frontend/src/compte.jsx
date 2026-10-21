import { useState } from "react";
import "./compte.css";

function Compte(){
    return(
        <main className="main_compte">
            <header className="header_compte">
                <div>
                    <img src="../static/icon/logo_jirama.jpg" alt="J" />
                    <p>GESTION DES COMPTES DES EMPLOYES</p>
                </div>
                
                <div>
                    <div>ANDRIANINA RAZAFINDRASATA . ADMIN</div>
                    <img src="../static/icon/logout.png" alt="D" />
                </div>
            </header>
            <div className="body_compte">
                <section className="section_compte"></section>
                <nav className="nav_compte"></nav>  
            </div>
        </main>
    )
}

export default Compte;
