import { Component, Input} from '@angular/core';

import { Product } from './prototypes';
import { KiwoomService } from './app.service';



@Component({
    selector: 'chart',
    template: require('./chart.component.html')
})

export class ChartComponent{
    
    @Input()
    product: Product;
    
    //bokeh:any;
    data_doc:any;
    chartdata:any;
    
    constructor(
        private kiwoomService: KiwoomService
    ) {}
    

    ngAfterViewInit(){
        (<any>window).tmp = this.product;
        //construct chart
	    this.bokeh = (<any>window).Bokeh;
        this.bokeh.set_log_level("info");
        
        let chartJson = require('json!./chart.component.json');
        let docs_json = chartJson.docs_json;
        let render_items = chartJson.render_items;

        this.bokeh.$(()=> {
            let docs_json = chartJson.docs_json;
            let render_tiems = chartJson.render_items;
        });
        this.bokeh.embed.embed_items(docs_json, render_items);

        let id = this.bokeh._.keys(this.bokeh.index)[0];
        //this.data_doc = this.bokeh.index[id].model.document._all_models_by_name
        //                    ._dict['ohlc'][0];
        this.data_doc = this.bokeh.index[id].model.document.get_model_by_name("ohlc");
    }

    updateChart(){
        if (this.data_doc){
            //let data = this.data_doc.get('data');
            let data = this.data_doc.get('data')
            for (let field in data){
                data[field] = [];
            }
            for (let i=0; i< this.product.chart.length; i++){
                let close = this.product.chart[i][0];
                let open = this.product.chart[i][1];
                let high = this.product.chart[i][2];
                let low = this.product.chart[i][3];
                let date = this.product.chart[i][4];
                let volume = this.product.chart[i][5];
                let mid = (open+close)/2;
                let spans = Math.abs(open-close);
                let color:string;
                open < close? color='red' : color='blue';
                
                data.close.push(close);
                data.open.push(open);
                data.high.push(high);
                data.low.push(low);
                data.date.push(date);
                data.volume.push(volume);
                data.mid.push(mid);
                data.spans.push(spans);
                data.color.push(color);
            }
            this.data_doc.trigger('change');
        }
    }

    test(){
        console.log(this.product);
    }

    asdftest(){
        let docs_json:any;
        let ref_number:number;
        for (let i of docs_json[Object.keys(docs_json)[0]].roots.references){
            if (i.type == 'ColumnDataSource'){
                ref_number = docs_json[Object.keys(docs_json)[0]].roots.references.indexOf(i);
            }
        }

        let my_data = docs_json[Object.keys(docs_json)[0]].roots.references[ref_number].attributes.data

        my_data.low = [88.94, 91.12, 93.87, 90.12, 91.94, 91.0, 95.0, 99.5, 97.5, 95.12];
        my_data.open = [90.94, 92.12, 97.87, 95.12, 92.94, 92.0, 98.0, 99.5, 98.5, 96.12];
        my_data.close = [92.94, 94.12, 95.87, 93.12, 96.94, 93.0, 97.0, 100.5, 99.5, 98.12];
        my_data.high = [94.09, 95.37, 98.87, 97.37, 97.5, 96.19, 100.0, 102.5, 100.25, 99.25];
        my_data.date = [951868800000, 951955200000, 952041600000, 952300800000, 952387200000, 952473600000, 952560000000, 952646400000, 952905600000, 952992000000];
        my_data.volume = [88.94, 91.12, 93.87, 90.12, 91.94, 91.0, 95.0, 99.5, 97.5, 95.12];
    
        for (let i=0; i<10 ; i++) {
            if (my_data.open[i] >= my_data.close[i]) {
                my_data.color[i] = 'blue';
            } else {
                my_data.color[i] = 'red';
            }
        }
    }

}