import { Component, ViewChild, ElementRef} from '@angular/core';
import { CommonService } from './app.service';

declare var Highcharts:any;

@Component({
  selector: 'my-overview',
  template: require('./overview.component.html'),
})

export class OverviewComponent{
  recordDB:any;
  
  @ViewChild('chartDiv')
  chartDiv: ElementRef;

  ngOnInit() {
    //historyDB object 로드 끝날때까지 기다림
    if (( < any > window).recordDB == undefined) {
      setTimeout(() => {
        this.ngOnInit();
      }, 100);
    } else {
      this.recordDB = (<any>window).recordDB;
      this.getData();
    }
  }

  getData() {
    this.recordDB.getAllData().then( (data:any)=> {
        this.drawChart(data);
    });
  }

  drawChart(el:any) {
    let data = el.profit
    let ohlc:any[] = [],
        volume:any[] = [],
        dataLength = data.length,
            // set the allowed units for data grouping
            groupingUnits = [[
                'day',                         // unit name
                [1]                             // allowed multiples
            ], [
                'month',
                [1, 2, 3, 4, 6]
            ]],

            i = 0;

        for (i; i < dataLength; i += 1) {
            ohlc.push([
                data[i][0], // the date
                data[i][1], // open
                data[i][2], // high
                data[i][3], // low
                data[i][4] // close
            ]);

            volume.push([
                data[i][0], // the date
                data[i][5] // the volume
            ]);
        }

    Highcharts.stockChart(this.chartDiv.nativeElement, {

            rangeSelector: {
                selected: 1
            },

            title: {
                text: 'AAPL Historical'
            },

            yAxis: [{
                labels: {
                    align: 'right',
                    x: -3
                },
                title: {
                    text: 'OHLC'
                },
                height: '60%',
                lineWidth: 2
            }, {
                labels: {
                    align: 'right',
                    x: -3
                },
                title: {
                    text: 'Volume'
                },
                top: '65%',
                height: '35%',
                offset: 0,
                lineWidth: 2
            }],

            tooltip: {
                split: true
            },

            series: [{
                type: 'candlestick',
                name: 'AAPL',
                data: ohlc,
                dataGrouping: {
                    units: groupingUnits
                }
            }, {
                type: 'column',
                name: 'Volume',
                data: volume,
                yAxis: 1,
                dataGrouping: {
                    units: groupingUnits
                }
            }]
        });
  }
}
  

