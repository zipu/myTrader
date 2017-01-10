import { Component, ViewChild, ElementRef} from '@angular/core';
import { CommonService } from './app.service';

declare var Highcharts:any;

@Component({
  selector: 'my-overview',
  template: require('./overview.component.html'),
  styles: [require('./overview.component.css')],
})

export class OverviewComponent{
  recordDB:any;
  equityChart:any;
  compChart: any;
  freqChart: any;
  
  @ViewChild('equityDiv')
  equityDiv: ElementRef;

  @ViewChild('compDiv')
  compDiv: ElementRef;

  @ViewChild('freqDiv')
  freqDiv:any;

  ngOnInit() {
    //historyDB object 로드 끝날때까지 기다림
    if (( < any > window).recordDB == undefined) {
      setTimeout(() => {
        this.ngOnInit();
      }, 100);
    } else {
      this.recordDB = (<any>window).recordDB;
      //highchart global option 
      Highcharts.setOptions({
        global: {
            timezoneOffset: -8 * 60 //중국 UTC +8:00 
        }
      });
      this.getData();
    }
  }

  getData() {
    this.recordDB.getAllData().then( (source:any)=> {
        this.drawEquityChart(source);
        this.drawCompChart(source);
        this.drawFreqChart(source);
        console.log(source);
    });
  }

  drawEquityChart(source:any) {
    this.equityChart = Highcharts.stockChart(this.equityDiv.nativeElement, {

            rangeSelector : {
                enabled: false 
            },
            title: {
                text: 'Equity Curve'
            },

            yAxis: [{
                labels: {
                    align: 'left',
                    x: 3
                },
                title: {
                    text: 'Profit'
                },
                height: '80%',
                lineWidth: 2
            }, {
                labels: {
                    align: 'left',
                    x: 3
                },
                title: {
                    text: 'Volume'
                },
                top: '80%',
                height: '20%',
                offset: 0,
                lineWidth: 2
            }],

            tooltip: {
                split: true
            }, 
            navigator: {
                enabled: false,
                height: 20
            },
            scrollbar: {
                enabled: false
            },

            series: [{
                type: 'candlestick',
                name: 'Profit',
                data: source.profitOHLC,
                dataGrouping: {
                    forced: true,
                    units: [['day',[1]]]
                }
            }, {
                type: 'column',
                name: 'Volume',
                data: source.volume,
                yAxis: 1,
                dataGrouping: {
                    approximation: "sum",
                    forced: true,
                    units: [['day',[1]]]
                }
            }, {
                type: 'line',
                name: 'commission',
                data: source.commission,
                yAxis: 0,
                dataGrouping: {
                    approximation: this.get_last,
                    forced: true,
                    units: [['day',[1]]]
                }
            }],

        });
  }


  drawFreqChart(source:any){
      Highcharts.chart(this.freqDiv.nativeElement, {
          chart: {
              type: 'column'
          },
          title: {
              text: 'Distribution'
          },
          xAxis: {
              gridLineWidth: 1,
          },
          yAxis: {
              labels: {
                    align: 'left',
                    x: 3
              },
              title: {
                  text: 'Percent (%)'
              }
          },
          legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
            x: 0,
            y: 30,
            floating: true,
          },
          series: [{
              name: 'Ticks',
              type: 'column',
              data: source.freq_ticks,
              pointPadding: 0,
              groupPadding: 0,
              pointPlacement: 'on'
          }]
      });
    }

    

    drawCompChart(source:any){
      let custom = function(arr:any){
            return arr.length ? arr[arr.length - 1] : (arr.hasNulls ? null : undefined);
      }
      this.compChart = Highcharts.stockChart(this.compDiv.nativeElement, {
          rangeSelector : {
                enabled: false 
          },
          navigator: {
                enabled: false,
          },
          scrollbar: {
                enabled: false
          },
          title: {
              text: 'Comparison'
          },
          yAxis: {
              labels: {
                    align: 'left',
                    x: 3
              },
              opposite: false,
              title: {
                  text: 'Percent (%)'
              }
          },
          series: [{
              name: 'profit',
              data: source.profit,
              dataGrouping: {
                    approximation: this.get_last,
                    forced: true,
                    units: [['day',[1]]]
                }
          },{
              name: 'ticks',
              data: source.ticks,
              dataGrouping: {
                    approximation: this.get_last,
                    forced: true,
                    units: [['day',[1]]]
                }
          },{
              name: 'cum winrate',
              color: '#b54edb',
              data: source.winrate,
              dataGrouping: {
                    approximation: this.get_last,
                    forced: true,
                    units: [['day',[1]]]
              }
          },{
              name: 'winrate',
              type: 'column',
              data: source.result,
              visible: false,
              color: '#c5e2dd',
              dataGrouping:{
                  approximation: function(arr:any){
                      let rate: number;
                      if (arr.length > 0) {
                        let tot = arr.reduce( (a:number,b:number) => {
                            return a+b;
                        });
                        rate = (tot/arr.length) * 100;
                        rate = Number(rate.toFixed(2));
                      } else {
                        rate = 0;
                      }
                      return rate;
                  },
                  forced: true, 
                  units: [['day',[1]]]
              },
              zIndex: -1
          }]
      });
    }

    //차트 타임프레임 변경하는 함수
    timeFrame(unit:string, flag:number){
      let newOption:any = {};
      if (unit == "tick") {  //tick chart - no data grouping 
          newOption = {
              enabled: false
          }
         //this.profitChart.series[1].update({dataGrouping:{enabled:false}}); //모르겠음 이거 있어야 수수료차트 grouping 꺼짐
      } else {  
          newOption = {
              enabled: true,
              forced: true,
              units: [[unit,[1]]]
          }
      }

      if (flag == 1) { //equity chart
          this.equityChart.series[0].update({dataGrouping: newOption}); //profit data
          this.equityChart.series[1].update({dataGrouping: newOption}); //commission data
          this.equityChart.series[2].update({dataGrouping: newOption}); //volume data
      } else if (flag == 2) { //Comparison chart
          this.compChart.series[0].update({dataGrouping: newOption}); //normalized tick
          this.compChart.series[1].update({dataGrouping: newOption}); //normalized profit
          this.compChart.series[2].update({dataGrouping: newOption}); //winrate
          if (unit == "day") {
            this.compChart.series[3].update({visible:false});
          } else {
            this.compChart.series[3].update({visible:true, dataGrouping: newOption});
          }
      }
    }

    //data grouping approximation method
    get_last(arr:any){
        return arr.length ? arr[arr.length - 1] : (arr.hasNulls ? null : undefined);
    }

}
  

