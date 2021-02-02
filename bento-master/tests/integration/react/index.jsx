import React from 'react';
import ReactDOM from 'react-dom';


class App extends React.Component {
    render() {
        if (this.props.ignore) return null;
        return (
            <div><a/>My Flask React App!</div>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
