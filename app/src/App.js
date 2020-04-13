import React, { Component } from "react";
import "./App.css";
import axios from "axios";
import { FixedSizeList as List } from "react-window";
import AutoSizer from "react-virtualized-auto-sizer";
import "react-virtualized/styles.css";

class App extends Component {
  constructor() {
    super();
    this.state = {
      data: [],
      gotData: false,
      currentLoc: "Lillesand",
      currentIndex: 666,
      currentScore: 69,
    };
  }

  async componentDidMount() {
    const response = await axios.get("http://85.164.172.93:8888/");
    console.log(response);
    const data = await response.data;
    this.setState({ data: data, gotData: true });
    var main = document.getElementById("main");
    main.style.height = window.innerHeight - 160 + "px";
    // var listelement = document.getElementById("listelement");
    var list = document.getElementById("list");
    list.style.width = window.innerWidth - 300 + "px";
    var head = document.getElementById("categories");
    head.style.width = window.innerWidth - 300 + "px";
  }

  Row = ({ index, style }) => (
    <div id="listelement" style={style}>
      <div class="elementelement" id="rank">
        {index}
      </div>
      <div class="elementelement" id="location">
        {this.state.data[index].location}
      </div>
      <div class="elementelement" id="score">
        {this.state.data[index].kjipestScore.toFixed(2)}
      </div>
      <div class="elementelement" id="icon">
        <img src={require("./img/bw/rain.svg")} alt="" />
      </div>
    </div>
  );

  KjipestList() {
    return (
      <div style={{ display: "flex" }}>
        <div style={{ flex: "1 1 auto", height: "73vh" }}>
          <AutoSizer>
            {({ height, width }) => (
              <List
                className="List"
                height={height}
                itemCount={this.state.data.length}
                itemSize={80}
                width={width}
              >
                {this.Row}
              </List>
            )}
          </AutoSizer>
        </div>
      </div>
    );
  }

  renderPage() {
    return (
      <div>
        <div>
          <nav>
            <div class="nav" id="search">
              <input type="search" name="search" placeholder="søk" value="" />
            </div>
            <div class="nav" id="navlist">
              <h2>Liste</h2>
            </div>
            <div class="nav">
              <h2>Kart</h2>
            </div>
            <div class="nav">
              <h2>Info</h2>
            </div>
          </nav>
        </div>

        <div class="subheader">
          <div id="categories">
            <div class="head" id="crank">
              <h3>Rangering</h3>
            </div>
            <div class="head" id="cloc">
              <h3>Sted</h3>
            </div>
            <div class="head" id="cscore">
              <h3>Kjipest – Minst kjipt ↓</h3>
            </div>
            <div class="head" id="cicon">
              <h3>Værtype</h3>
            </div>
          </div>

          <div id="locName">
            <p>{this.state.currentLoc}</p>
            <h3>(Din posisjon)</h3>
          </div>
        </div>

        <div id="main">
          <div id="list">{this.KjipestList()}</div>
          <div class="sidebar">
            <div class="localinfo">
              <div id="localscore">
                <h3>Score:</h3>
                <h1>{this.state.currentScore}</h1>
              </div>
              <img src={require("./img/c/partlycloudy.svg")} alt="" />
              <div class="localrank">
                <h3>Rangering:</h3>
                <h1>{this.state.currentIndex}</h1>
              </div>
            </div>
            <div class="logo">
              <img src={require("./img/logo.svg")} alt="" />
            </div>
          </div>
        </div>
        <script type="text/javascript" src="./script.js" />
      </div>
    );
  }

  useEffect() {
    function handleResize() {
      var main = document.getElementById("main");
      main.style.height = window.innerHeight - 160 + "px";
      var list = document.getElementById("list");
      list.style.width = window.innerWidth - 300 + "px";
      var head = document.getElementById("categories");
      head.style.width = window.innerWidth - 300 + "px";
      window.addEventListener("resize", handleResize);
      return (_) => {
        window.removeEventListener("resize", handleResize);
      };
    }
  }

  render() {
    if (this.state.gotData) {
      return <div>{this.renderPage()}</div>;
    } else {
      return <div></div>;
    }
  }
}

export default App;
