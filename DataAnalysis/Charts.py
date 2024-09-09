import os

import matplotlib.pyplot as plt
import matplotlib as mpl
import statistics

import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay

from Configuration import Configuration
import numpy as np

from FileOperations import FileOperations

mpl.rcParams['figure.dpi'] = 600


class Charts:
    # ColorPalette=['lime','deepskyblue', 'darkorange', 'red']
    ColorPalette = ['tab:red', 'tab:blue', 'tab:orange', 'tab:green']

    @staticmethod
    def BarChartWithBox(data, x_title, y_title, directory, filename, func=statistics.median, showBoxPlot=False,
                                   ylim=None, legend_loc='best', labels=None):
        #LC, NB, LR, MLP, SVM, RF, XGB
        #labels = ['LC', 'DT', 'KNN', 'MLP', 'SVM', 'RF', 'XGB']
        median_values = [0, 0, 0, 0,0]
        if Configuration.ShowBar:
            median_values = [func(data[label]) for label in labels]



        x = np.arange(len(labels))  # the label locations
        width = 0.80  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x, median_values, width, color=Charts.ColorPalette[1])


        if showBoxPlot:
            boxplot_data = [data[label] for label in labels]


            box1 = ax.boxplot(boxplot_data, widths=width, positions=x, showfliers=False,
                              showbox=Configuration.ShowBox, patch_artist=True)

            plt.setp(box1["boxes"], facecolor=Charts.ColorPalette[2])
            color = 'violet'

            plt.setp(box1["medians"], color=color)
            plt.setp(box1["whiskers"], color=color)
            plt.setp(box1["caps"], color=color)

        if ylim is not None:
            ax.set_ylim(ylim)

        Charts.autolabel(rects1, ax)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(y_title)
        if x_title is not None:
            ax.set_xlabel(x_title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        #ax.legend(loc=legend_loc)

        fig.tight_layout()
        if Configuration.Save:
            Charts.SaveFigure(plt, directory, filename)
        else:
            plt.show()
        Charts.ClearFigure()

    @staticmethod
    def CPU_Memory_BoxSimple(cpu, memory, x_title, y_title, directory, filename, func=statistics.median, showBoxPlot=False,
                                    ylim=None, legend_loc='best', labels=None):


        cpu_median = [0]*len(labels)
        memory_median =[0]*len(labels)
        if Configuration.ShowBar:
            cpu_median = [func(cpu[label]) for label in labels]
            memory_median = [func(memory[label]) for label in labels]


        x = np.arange(len(labels))  # the label locations
        width = 0.30  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width / 2, cpu_median, width, label='CPU Usage',
                        color=Charts.ColorPalette[1])
        rects2 = ax.bar(x + width / 2, memory_median, width, label='Memory Usage', color=Charts.ColorPalette[0])

        if showBoxPlot:
            cpu_data = [cpu[label] for label in labels]
            memory_data = [memory[label] for label in labels]

            box1 = ax.boxplot(cpu_data, widths=width, positions=x - width / 2, showfliers=False,
                              showbox=Configuration.ShowBox, patch_artist=True)
            box2 = ax.boxplot(memory_data, widths=width, positions=x + width / 2, showfliers=False,
                              showbox=Configuration.ShowBox, patch_artist=True)

            plt.setp(box1["boxes"], facecolor=Charts.ColorPalette[2])
            plt.setp(box2["boxes"], facecolor=Charts.ColorPalette[1])
            color = 'violet'

            plt.setp(box1["medians"], color=color)
            plt.setp(box2["medians"], color=color)
            plt.setp(box1["whiskers"], color=color)
            plt.setp(box2["whiskers"], color=color)
            plt.setp(box1["caps"], color=color)
            plt.setp(box2["caps"], color=color)

        if ylim is not None:
            ax.set_ylim(ylim)

        Charts.autolabel(rects1, ax)
        Charts.autolabel(rects2, ax)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(y_title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend(loc=legend_loc)

        fig.tight_layout()
        if Configuration.Save:
            Charts.SaveFigure(plt, directory, filename)
        else:
            plt.show()
        Charts.ClearFigure()


    @staticmethod
    def PlotLineGraph(x, y, x_label, y_label, directory, filename):
        xpoints = np.array(x)
        ypoints = np.array(y)
        plt.plot(xpoints, ypoints, Configuration.Colors[0])
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        if Configuration.Save:
            Charts.SaveFigure(plt, directory, filename)
            Charts.WriteLineGraphData([x, y], [x_label, y_label], directory, filename)
        else:
            plt.show()
        Charts.ClearFigure()

    @staticmethod
    def BoxPlot(data, labels, x_title, y_title, directory, filename):
        fig, ax = plt.subplots()
        # Create an axes instance
        # ax = fig.add_axes([0,0,1,1])
        bp = ax.boxplot(data, showfliers=True)
        plt.xticks([x + 1 for x in range(len(labels))], labels)
        plt.xlabel(x_title)
        plt.ylabel(y_title)
        if Configuration.Save:
            Charts.SaveFigure(plt, directory, filename)
            Charts.WriteLineGraphData(data, labels, directory, filename)
        else:
            plt.show()
        Charts.ClearFigure()

    @staticmethod
    def PlotLineCharts(data, labels, x_title, y_title, directory, filename,folders):

        count =0
        for i in range(len(data)):
            sample = data[i]
            mean = np.mean(sample)

            if mean*1000> 0.3:
                count=count+1
                print(f"counter: {i}, mean: {mean}, filename: {folders[i]}")

        print(f"count: {count}")

        return
            # pass
            # fig, ax = plt.subplots()
            # lg = ax.plot(sample)
            # plt.xlabel(x_title)
            # plt.ylabel(y_title)
            # if Configuration.Save:
            #     Charts.SaveFigure(plt, directory+ filename+'/',f"{counter:03d}")
            #     Charts.WriteLineGraphData(data, labels, directory, filename)
            # else:
            #     plt.show()
            #
            #
            #
            # Charts.ClearFigure()






    @staticmethod
    def GroupedBoxSimpleFull(data, x_title, y_title, directory, filename, func=statistics.median, showBoxPlot=False,
                             ylim=None, legend_loc='best'):

        temp = plt.rcParams["figure.figsize"]
        plt.rcParams["figure.figsize"] = [temp[0], temp[1]*1.23]
        labels = ['Discovery and connection\nto worker (Wi-Fi)', 'Connection to worker\n(Wi-Fi)', 'Connection to broker\n(Wi-Fi)', 'Connection to cloud\n(Wi-Fi)', 'Discovery and connection\nto worker (LTE)', 'Connection to cloud\n(LTE)']
        actual_client_median =  mock_client_wifi_median = [0, 0, 0, 0, 0]
        if Configuration.ShowBar:
            actual_client_median = [func(data['ActualClient']['WiFi']),
                              func(data['ActualClient']['Worker']),
                              func(data['ActualClient']['Broker']),
                              func(data['ActualClient']['Cloud']),
                              func(data['ActualClient']['LTE']),
                              func(data['ActualClient']['LTE_Cloud'])
                              ]
            mock_client_wifi_median = [func(data['MockClient']['WiFi']),
                                      func(data['MockClient']['Worker_WiFi']),
                                      func(data['MockClient']['Broker_WiFi']),
                                      func(data['MockClient']['Cloud_WiFi']),
                                      func(data['MockClient']['LTE']),
                                      func(data['MockClient']['LTE_Cloud'])
                                      ]

        x = np.arange(len(labels))  # the label locations
        width = 0.30  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width / 2, mock_client_wifi_median, width, label='Mock Client', color=Charts.ColorPalette[1])
        rects2 = ax.bar(x + width / 2, actual_client_median, width, label='Actual Client', color=Charts.ColorPalette[0])

        if showBoxPlot:
            actual_client_data = [data['ActualClient']['WiFi'], data['ActualClient']['Worker'],
                            data['ActualClient']['Broker'], data['ActualClient']['Cloud'], data['ActualClient']['LTE'], data['ActualClient']['LTE_Cloud']]

            wifi_data = [
                data['MockClient']['WiFi'],
                data['MockClient']['Worker_WiFi'],
                data['MockClient']['Broker_WiFi'],
                data['MockClient']['Cloud_WiFi'],
                data['MockClient']['LTE'],
            data['MockClient']['LTE_Cloud']]
            box1 = ax.boxplot(wifi_data, widths=width, positions=x - width / 2, showfliers=False,
                              showbox=Configuration.ShowBox, patch_artist=True)
            box2 = ax.boxplot(actual_client_data, widths=width, positions=x + width / 2, showfliers=False,
                              showbox=Configuration.ShowBox, patch_artist=True)

            plt.setp(box1["boxes"], facecolor=Charts.ColorPalette[2])
            plt.setp(box2["boxes"], facecolor=Charts.ColorPalette[1])
            color = 'violet'

            plt.setp(box1["medians"], color=color)
            plt.setp(box2["medians"], color=color)
            plt.setp(box1["whiskers"], color=color)
            plt.setp(box2["whiskers"], color=color)
            plt.setp(box1["caps"], color=color)
            plt.setp(box2["caps"], color=color)

        if ylim is not None:
            ax.set_ylim(ylim)

        Charts.autolabel(rects1, ax)
        Charts.autolabel(rects2, ax)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(y_title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', rotation_mode='anchor', multialignment="center")
        ax.legend(loc=legend_loc)

        fig.tight_layout()
        if Configuration.Save:
            Charts.SaveFigure(plt, directory, filename)
        else:
            plt.show()
        Charts.ClearFigure()
        plt.rcParams["figure.figsize"]=temp

    @staticmethod
    def GroupedBoxSimple(data, x_title, y_title, directory, filename, func=statistics.median, showBoxPlot=False,
                         ylim=None, legend_loc='best'):

        labels = ['Worker\n(Wi-Fi)', 'Broker\n(Wi-Fi)', 'Cloud\n(Wi-Fi)', 'Worker\n(LTE)', 'Cloud\n(LTE)']
        actual_client_median =  mock_client_wifi_median = [0, 0, 0, 0]
        if Configuration.ShowBar:
            actual_client_median = [
                func(data['ActualClient']['Worker']),
                func(data['ActualClient']['Broker']),
                func(data['ActualClient']['Cloud']),
                func(data['ActualClient']['LTE']),
                func(data['ActualClient']['LTE_Cloud'])
            ]
            mock_client_wifi_median = [
                func(data['MockClient']['Worker_WiFi']),
                func(data['MockClient']['Broker_WiFi']),
                func(data['MockClient']['Cloud_WiFi']),
                func(data['MockClient']['LTE']),
                func(data['MockClient']['LTE_Cloud'])
            ]

        x = np.arange(len(labels))  # the label locations
        width = 0.30  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width / 2, mock_client_wifi_median, width, label='Mock Client',
                        color=Charts.ColorPalette[1])
        rects2 = ax.bar(x + width / 2, actual_client_median, width, label='Actual Client', color=Charts.ColorPalette[0])

        if showBoxPlot:
            actual_client_data = [data['ActualClient']['Worker'],
                            data['ActualClient']['Broker'], data['ActualClient']['Cloud'], data['ActualClient']['LTE'],data['ActualClient']['LTE_Cloud']]

            wifi_data = [
                data['MockClient']['Worker_WiFi'],
                data['MockClient']['Broker_WiFi'],
                data['MockClient']['Cloud_WiFi'],
                data['MockClient']['LTE'],
                data['MockClient']['LTE_Cloud']
            ]
            box1 = ax.boxplot(wifi_data, widths=width, positions=x - width / 2, showfliers=False,
                              showbox=Configuration.ShowBox, patch_artist=True)
            box2 = ax.boxplot(actual_client_data, widths=width, positions=x + width / 2, showfliers=False,
                              showbox=Configuration.ShowBox, patch_artist=True)

            plt.setp(box1["boxes"], facecolor=Charts.ColorPalette[2])
            plt.setp(box2["boxes"], facecolor=Charts.ColorPalette[1])
            color = 'violet'

            plt.setp(box1["medians"], color=color)
            plt.setp(box2["medians"], color=color)
            plt.setp(box1["whiskers"], color=color)
            plt.setp(box2["whiskers"], color=color)
            plt.setp(box1["caps"], color=color)
            plt.setp(box2["caps"], color=color)

        if ylim is not None:
            ax.set_ylim(ylim)

        Charts.autolabel(rects1, ax)
        Charts.autolabel(rects2, ax)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(y_title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend(loc=legend_loc)

        fig.tight_layout()
        if Configuration.Save:
            Charts.SaveFigure(plt, directory, filename)
        else:
            plt.show()
        Charts.ClearFigure()






    @staticmethod
    def Resource_GroupedBox_Simple(data, x_title, y_title, directory, filename, func=statistics.median, showBoxPlot=False,
                            ylim=None, legend_loc='best'):

        labels = ['Worker\n(Wi-Fi)', 'Broker\n(Wi-Fi)', 'Cloud\n(Wi-Fi)', 'Proxy\n(LTE)', 'Worker\n(LTE)', 'Cloud\n(LTE)']
        median_values = [0, 0, 0, 0,0]
        if Configuration.ShowBar:
            median_values = [
                func(data['MockClient']['Worker_WiFi']),
                func(data['MockClient']['Broker_WiFi']),
                func(data['MockClient']['Cloud_WiFi']),
                func(data['MockClient']['Broker_LTE']),
                func(data['MockClient']['Worker_LTE']),
                func(data['MockClient']['LTE_Cloud'])
            ]


        x = np.arange(len(labels))  # the label locations
        width = 0.80  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x, median_values, width, color=Charts.ColorPalette[1])


        if showBoxPlot:
            wifi_data = [data['MockClient']['Worker_WiFi'],
                             data['MockClient']['Broker_WiFi'], data['MockClient']['Cloud_WiFi'],
                             data['MockClient']['Broker_LTE'], data['MockClient']['Worker_LTE'], data['MockClient']['LTE_Cloud']]

            box1 = ax.boxplot(wifi_data, widths=width, positions=x, showfliers=False,
                              showbox=Configuration.ShowBox, patch_artist=True)

            plt.setp(box1["boxes"], facecolor=Charts.ColorPalette[2])
            color = 'violet'

            plt.setp(box1["medians"], color=color)
            plt.setp(box1["whiskers"], color=color)
            plt.setp(box1["caps"], color=color)

        if ylim is not None:
            ax.set_ylim(ylim)

        Charts.autolabel(rects1, ax)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(y_title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        #ax.legend(loc=legend_loc)

        fig.tight_layout()
        if Configuration.Save:
            Charts.SaveFigure(plt, directory, filename)
        else:
            plt.show()
        Charts.ClearFigure()

    @staticmethod
    def autolabel(rects, ax):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()

            if height != 0:
                ax.annotate('{:.1f}'.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom',

                            )

    @staticmethod
    def CPU_Memory_GroupedBoxSimple(cpu, memory, x_title, y_title, directory, filename, func=statistics.median, showBoxPlot=False,
                         ylim=None, legend_loc='best'):

        labels = ['Worker\n(Wi-Fi)', 'Broker\n(Wi-Fi)', 'Cloud\n(Wi-Fi)', 'Proxy\n(LTE)', 'Worker\n(LTE)', 'Cloud\n(LTE)']
        cpu_median  = [0, 0, 0, 0,0,0]
        if Configuration.ShowBar:
            cpu_median = [
                func(cpu['MockClient']['Worker_WiFi']),
                func(cpu['MockClient']['Broker_WiFi']),
                func(cpu['MockClient']['Cloud_WiFi']),
                func(cpu['MockClient']['Broker_LTE']),
                func(cpu['MockClient']['Worker_LTE']),
                func(cpu['MockClient']['LTE_Cloud'])
            ]
            memory_median = [
                func(memory['MockClient']['Worker_WiFi']),
                func(memory['MockClient']['Broker_WiFi']),
                func(memory['MockClient']['Cloud_WiFi']),
                func(memory['MockClient']['Broker_LTE']),
                func(memory['MockClient']['Worker_LTE']),
                func(memory['MockClient']['LTE_Cloud'])
            ]

        x = np.arange(len(labels))  # the label locations
        width = 0.30  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width / 2, cpu_median, width, label='CPU Usage',
                        color=Charts.ColorPalette[1])
        rects2 = ax.bar(x + width / 2, memory_median, width, label='Memory Usage', color=Charts.ColorPalette[0])

        if showBoxPlot:
            cpu_data = [cpu['MockClient']['Worker_WiFi'],
                cpu['MockClient']['Broker_WiFi'],
                cpu['MockClient']['Cloud_WiFi'],
                cpu['MockClient']['Broker_LTE'],
                cpu['MockClient']['Worker_LTE'],
                cpu['MockClient']['LTE_Cloud']]

            memory_data = [
                memory['MockClient']['Worker_WiFi'],
                memory['MockClient']['Broker_WiFi'],
                memory['MockClient']['Cloud_WiFi'],
                memory['MockClient']['Broker_LTE'],
                memory['MockClient']['Worker_LTE'],
                memory['MockClient']['LTE_Cloud']
            ]
            box1 = ax.boxplot(cpu_data, widths=width, positions=x - width / 2, showfliers=False,
                              showbox=Configuration.ShowBox, patch_artist=True)
            box2 = ax.boxplot(memory_data, widths=width, positions=x + width / 2, showfliers=False,
                              showbox=Configuration.ShowBox, patch_artist=True)

            plt.setp(box1["boxes"], facecolor=Charts.ColorPalette[2])
            plt.setp(box2["boxes"], facecolor=Charts.ColorPalette[1])
            color = 'violet'

            plt.setp(box1["medians"], color=color)
            plt.setp(box2["medians"], color=color)
            plt.setp(box1["whiskers"], color=color)
            plt.setp(box2["whiskers"], color=color)
            plt.setp(box1["caps"], color=color)
            plt.setp(box2["caps"], color=color)

        if ylim is not None:
            ax.set_ylim(ylim)

        Charts.autolabel(rects1, ax)
        Charts.autolabel(rects2, ax)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(y_title)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend(loc=legend_loc)

        fig.tight_layout()
        if Configuration.Save:
            Charts.SaveFigure(plt, directory, filename)
        else:
            plt.show()
        Charts.ClearFigure()


    @staticmethod
    def WriteLineGraphData(value_arrays, headers, directory, filename):
        merged_list = list(zip(*value_arrays))
        df = pd.DataFrame(merged_list, columns=headers)
        df.to_csv(directory + filename + ".csv", sep=";")
        a = 1

    @staticmethod
    def ClearFigure():
        plt.figure().clear()
        plt.close('all')
        plt.cla()
        plt.clf()

    @staticmethod
    def SaveFigure(plt, directory, name):
        os.makedirs(directory, exist_ok=True)
        path = directory + name
        # plt.savefig(path + '.jpeg', bbox_inches='tight')
        plt.savefig(path + '.pdf', bbox_inches='tight')
        #plt.savefig(path + '.eps', bbox_inches='tight', transparent=True)
        #plt.savefig(path + '.png', bbox_inches='tight')
        # plt.savefig(path + '.svg', bbox_inches='tight', format="svg", transparent=True)
        # plt.savefig(path + '.tiff', bbox_inches='tight')
