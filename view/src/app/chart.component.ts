import { Component, Input, ViewChild, ElementRef, SimpleChanges} from '@angular/core';
import { Product } from './prototypes';
import { KiwoomService } from './app.service';

declare var Highcharts: any;


@Component({
    selector: 'my-chart',
    template: require('./chart.component.html'),
    styles: [require('./chart.component.css')],
})

export class ChartComponent{
    
    @Input('product') product: Product;
    @Input('kiwoom') kiwoom: any;

    @ViewChild('densityDiv')
    densityDiv: ElementRef;

    densityChart:any;

    
    constructor(
        private kiwoomService: KiwoomService
    ) {}


    test() {
        console.log(this.densityChart.series[0].data[100])
        this.densityChart.series[0].data[100].select();
        
    }

    //변수 변경하여 차트를 다시 그림
    apply_changes() {
        
        //console.log(this.product.size);
        this.kiwoom.get_density_diff(this.product.size)
            .then( (data:any)=> {
                this.densityChart.series[1].update({data: data});
            });
    }

    setPriceOnChart() {
        console.log(this.densityChart.series[0])
        let price = Number(this.product.price);
        let index = this.densityChart.series[0].xData.indexOf(price);
        console.log(price, index)
        this.densityChart.series[0].data[index].select();
    }

    drawDensityChart(data:any) {
        this.densityChart = Highcharts.chart(this.densityDiv.nativeElement, {
            chart: {
                zoomType: 'x'
            },
            title: {
                text: 'Density Distribution'
            },

            xAxis: {
                crosshair: true,
                title: {
                    text: 'Price'
                },
                //allowDecimals: false,
                labels: {
                    formatter: function () {
                        return this.value; // clean, unformatted number for year
                    }
                },
            },
            yAxis: [{
                        title: {
                          text: 'Percent (%)'
                        },
                        labels: {
                        formatter: function () {
                             return this.value * 100 + '%';
                            }
                        },
                        height: '70%'
                    }, {
                        title: {
                          text: 'diff'
                        },
                        labels: {
                        formatter: function () {
                             return this.value;
                            }
                        },
                        plotLines: [{
                            color: 'blue',
                            width: 2,
                            value: 0
                        },{
                            color: 'red',
                            width: 2, 
                            value: 1 
                        },{
                            color: 'red',
                            width: 2, 
                            value: -1 
                        }],
                        top: '70%',
                        height: '30%',
                        offset: 0,
                        lineWidth: 1
                   }],
            
            tooltip: {
                split: true,
        
            },
    
            plotOptions: {
                
                area: {
                  //enableMouseTracking: false,
                  fillColor: {
                    linearGradient: {
                        x1: 0,
                        y1: 0,
                        x2: 0,
                        y2: 1
                    },
                    stops: [
                        [0, Highcharts.getOptions().colors[0]],
                        [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                    ]
                  },
                  marker: {
                      enabled: false
                  },
                  lineWidth: 1,
                  states: {
                      hover: {
                          lineWidth: 1
                      }
                  },
                  threshold: null
                }
            },
            legend: {
                enabled: false
            },
            series: [{
                  type: 'area',
                  name: 'density',
                  data: data.density,
                  yAxis: 0,
              }, {
                  type: 'line',
                  name: 'cumdiff-ratio',
                  data: data.density_diff,
                  yAxis: 1,
              }]
        });
    }

}