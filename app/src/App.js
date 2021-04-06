import React, { Component } from "react";
import "./App.css";
import axios from "axios";
import {FixedSizeList} from "react-window";
import { List, CellMeasurer, CellMeasurerCache } from 'react-virtualized';
import AutoSizer from "react-virtualized-auto-sizer";
import "react-virtualized/styles.css";
import Autocomplete from 'react-autocomplete'

class App extends Component {
  constructor() {
    super();
    this.cellHeightCache = new CellMeasurerCache({
      defaultHeight: 42,
      fixedWidth: true
    })
    this.state = {
      data: [],
      searchingFor: '',
      gotData: false,
      currentLoc: "Laster din posisjon",
      currentIndex: -1,
      currentScore: -1,
      flipList: false,
      orderText: "Kjipest – Minst kjipt ↓",
      locData: {},
      hasPos: false,
      lat: "",
      lon: ""
    };
  }
  listRef = React.createRef();

  async componentDidMount() {
    // const response = await axios.get("http://84.214.69.73:8888/");
    // const response = await axios.get("https://kjipest.no/sorted");
    const response = await axios.get("http://localhost:80/sorted");
    const data = await response.data;
    const dataWithId = data.map((currentItem, index) => {currentItem.index = index; return(currentItem)})
    this.setState({ data: dataWithId, gotData: true});
    var main = document.getElementById("main");
    main.style.height = window.innerHeight - 160 + "px";
    var list = document.getElementById("list");
    list.style.width = window.innerWidth - 300 + "px";
    var head = document.getElementById("categories");
    head.style.width = window.innerWidth - 300 + "px";
    if (navigator.geolocation) {
      async function getPosData(position){
        // const locresponse = await axios.get("http://84.214.69.73:8888/lonlat/" + position.coords.longitude + "&" + position.coords.latitude);
        // const locresponse = await axios.get("https://kjipest.no/lonlat/" + position.coords.longitude + "&" + position.coords.latitude);
        const locresponse = await axios.get("http://localhost:80/lonlat/" + position.coords.longitude + "&" + position.coords.latitude);
        const locData = await locresponse.data;
        let objWithId = dataWithId.find(o => o.location === locData.location);
        this.setState({ locData: locData, 
                        currentLoc: locData.location, currentIndex: objWithId.index, currentScore: locData.kjipestScore});
        this.setState({lat: position.coords.latitude, lon: position.coords.longitude, hasPos: true});
        };
      await navigator.geolocation.getCurrentPosition(getPosData.bind(this));
    }
  }

  Row = ({ index, style }) => {
    // If someone can make this not need weird logic for index = this.state.data.length, then I'll love you forever.
    if (this.state.flipList){
      if (this.state.data.length -index-3 > 0 ) {
        index = this.state.data.length-index-3;}
      else {
        index = 0;
      }}
    return (
    <div id="listelement" style={style}>
      <div className="elementelement" id="rank">
        {index+1}
      </div>
      <div className="elementelement" id="location">
        {this.state.data[index].location}
      </div>
      <div className="elementelement" id="score">
        {this.state.data[index].kjipestScore.toFixed(2)}
      </div>
      <div className="elementelement" id="icon">
        <img src={require("./img/bw/rain.svg")} alt="" />
      </div>
    </div>
  )};

  KjipestList() {
    return (
      <div style={{ display: "flex" }}>
        <div style={{ flex: "1 1 auto", height: "100vh" }}>
          <AutoSizer >
            {({ height, width }) => (
              <FixedSizeList
                className="List"
                height={height}
                itemCount={this.state.data.length}
                itemSize={80}
                width={width}
                ref={this.listRef}
                itemData={this.state.flipList}
              >
                {this.Row}
              </FixedSizeList>
            )}
          </AutoSizer>
        </div>
      </div>
    );
  }
  onSelect = (value, selection) => {
    if (this.state.flipList){
      this.listRef.current.scrollToItem(this.state.data.length - selection.index - 3, "start");
    } else{
      this.listRef.current.scrollToItem(selection.index, "start");
    }              
    this.setState({searchingFor: value});}

  renderItem = (item) => {
    return <div className='searchItem'>{item.location}</div>
  }

  renderMenu = (items, _, autocompleteStyle) => {
    this.cellHeightCache.clearAll()
    const rowRenderer = ({key, index, parent, style}) => {
      const Item = items[index]
      const onMouseDown = e => {
        if(e.button === 0) {
          Item.props.onClick(e)
        }
      }
      return (
        <CellMeasurer
          cache={this.cellHeightCache}
          key={key}
          parent={parent}
          rowIndex={index}
        >
          {React.cloneElement(Item, {
            style: style, 
            key: key, 
            onMouseEnter: null, 
            onMouseDown: onMouseDown
          })}
        </CellMeasurer>
      )
    }
    return (
      <List
        rowHeight={this.cellHeightCache.rowHeight}
        height={207}
        rowCount={items.length}
        rowRenderer={rowRenderer}
        width={autocompleteStyle.minWidth || 0}
        style={{
          //...customStyles,
          height: 'auto',
          maxHeight: '207px'
        }}
      />
    )
  }

  getLocalScore(){
    if (this.state.currentScore < 0){
      return "__"
    }else{
      return this.state.currentScore.toFixed(2)
    }
  }

  getLocalPercentage(){
    if (this.state.currentScore < 0){
      return ("__")
    }else{
      return ((this.state.currentIndex/this.state.data.length*100).toFixed(1).toString() + " %")
    }
  }

  renderPage() {
    const searchTerm = this.state.searchingFor;
    let data = searchTerm 
      ? this.state.data.filter(item =>
          item.location.toLowerCase().includes(searchTerm.toLowerCase())
        )
      : []
    return (
      <div>
        <div>
          <nav>
            <div className="nav" id="search">
              {/* <input type="search" name="search" placeholder="søk" value="" /> */}
              <Autocomplete
                items={data}
                value={this.state.searchingFor}
                
                renderItem={this.renderItem}
                renderMenu={this.renderMenu}
                
                getItemValue={ item => item.location }
                onChange={(e, value)=> this.setState({searchingFor: value})}
                onSelect={this.onSelect}
                inputProps={{ placeholder: 'søk' }}
              />
            </div>
            <div className="nav" id="navlist">
              <h2>Liste</h2>
            </div>
            <div className="nav">
              <h2>Kart</h2>
            </div>
            <div className="nav">
              <h2>Info</h2>
            </div>
          </nav>
        </div>

        <div className="subheader">
          <div id="categories">
            <div className="head" id="crank">
              <h3>Rangering</h3>
            </div>
            <div className="head" id="cloc">
              <h3>Sted</h3>
            </div>
            <div className="head" id="cscore">
              <h3 onClick={() => {
                                  if (this.state.flipList){
                                    this.setState({ orderText: "Kjipest – Minst kjipt ↓" ,
                                                    flipList: false});
                                    this.listRef.current.scrollToItem(0, "start");
                                  } else {
                                    this.setState({ orderText: "Kjipest – Minst kjipt ↑" ,
                                                    flipList: true});
                                    this.listRef.current.scrollToItem(0, "start");
                                  }}}>
      {this.state.orderText}</h3>
            </div>
            <div className="head" id="cicon">
              <h3>Værtyper</h3>
            </div>
          </div>

          <div id="locName">
            <p>{this.state.currentLoc}</p>
            <h3>(Din posisjon)</h3>
          </div>
        </div>

        <div id="main">
          <div id="list">{this.KjipestList()}</div>
          <div className="sidebar" >
            <div className="localinfo">
              <div id="localscore">
                <h3>Score:</h3>
                <h1>
                  {this.getLocalScore()}
                </h1>
              </div>
              <img src={require("./img/c/partlycloudy.svg")} alt="" />
              <div className="localrank">
                {/* <h3 className="localpercentage">Topp</h3> */}
                <h1 className="localpercentage">
                  {this.getLocalPercentage()}
                </h1>
                <h3 className="localpercentagebottom">av Norge har det kjipere enn deg</h3>
              </div>
            </div>
            <div className="logo">
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
    }
    return (_) => {
      window.removeEventListener("resize", handleResize);
    };
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
