import { Component, Input, ViewChild, ElementRef} from '@angular/core';
import { Product } from './prototypes';
import { KiwoomService } from './app.service';

declare var Highcharts: any;


@Component({
    selector: 'my-chart',
    template: require('./chart.component.html')
})

export class ChartComponent{
    
    @Input()
    product: Product;

    @ViewChild('densityDiv')
    densityDiv: ElementRef;

    densityChart:any;

    
    constructor(
        private kiwoomService: KiwoomService
    ) {}
    

    ngAfterViewInit(){
        //construct chart
        //this.drawDensityChart();
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
                title: {
                    text: 'Price'
                },
                //allowDecimals: false,
                labels: {
                    formatter: function () {
                        return this.value; // clean, unformatted number for year
                    }
                }
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
                        height: '80%'
                    }, {
                        title: {
                          text: 'diff'
                        },
                        labels: {
                        formatter: function () {
                             return this.value * 100 + '%';
                            }
                        },
                        top: '80%',
                        height: '20%'
                   }],
    
            plotOptions: {
                area: {
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
                      radius: 2
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
            series: [{
                  type: 'area',
                  name: this.product.name,
                  data: data.density,
                  yAxis: 0,
              }, {
                  type: 'line',
                  name: this.product.name,
                  data: data.density_diff,
                  yAxis: 1,
              }]
        });
    }

    

    updateChart(){
    }

    test(){
        console.log(this.product);
    }

}