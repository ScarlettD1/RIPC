using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Windows;
using WIA;

namespace RIPC_Scanner
{
    /// <summary>
    /// Логика взаимодействия для MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private DeviceManager deviceManager = new DeviceManager();
        private List<DeviceInfo> scanners = new List<DeviceInfo>();
        private string[] parametrs = ((App)Application.Current).Parameters;

        public MainWindow()
        {
            InitializeComponent();
            SetParametrs();
            GetScanners();
        }

        private void updateSButton_Click(object sender, RoutedEventArgs e)
        {
            GetScanners();
        }

        private void startScanButton_Click(object sender, RoutedEventArgs e)
        {
            Item scannerItem;
            // Подключение к сканеру
            try
            {
                var device = scanners[sComboBox.SelectedIndex].Connect();
                scannerItem = device.Items[1];
            }
            catch
            {
                GetScanners();
                return;
            }

            // Настройка необходимых параметров сканера
            scannerItem.Properties["6146"].set_Value(0);    // ЧБ цвет
            try
            {
                scannerItem.Properties["6147"].set_Value(300);    // DPI по горизонту
                scannerItem.Properties["6148"].set_Value(300);    // DPI по вертикали
            }
            catch
            {
                MessageBox.Show("Сканер не удовлетовряет требованиям!\nDPI 300", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);
                return;

            }

            bool multiscan = false;
            if (sAutoFeederCheckBox.IsChecked == true && sDuplexCheckBox.IsChecked == true)
            {
                try
                {
                    scannerItem.Properties["3088"].set_Value(5);    // Автоматическая подача документов + двухсторонее сканирование
                    multiscan = true;
                }
                catch
                {
                    MessageBox.Show("Сканер не поддерживает автоматичичскую подачу или двухсторонее сканирование.", "Информация", MessageBoxButton.OK, MessageBoxImage.Information, MessageBoxResult.Yes);
                    return;
                }
            }
            else if (sAutoFeederCheckBox.IsChecked == true)
            {
                try
                {
                    scannerItem.Properties["3088"].set_Value(4);    // Автоматическая подача документов
                    multiscan = true;
                }
                catch
                {
                    multiscan = false;
                    MessageBox.Show("Сканер не поддерживает автоматичичскую подачу.", "Информация", MessageBoxButton.OK, MessageBoxImage.Information, MessageBoxResult.Yes);
                    return;
                }
            }
            else if (sDuplexCheckBox.IsChecked == true)
            {
                try
                {
                    scannerItem.Properties["3088"].set_Value(2);    // Двухсторонее сканирование документов
                    multiscan = true;
                }
                catch
                {
                    multiscan = false;
                    MessageBox.Show("Сканер не поддерживает двухсторонее сканирование.", "Информация", MessageBoxButton.OK, MessageBoxImage.Information, MessageBoxResult.Yes);
                    return;
                }
            }
            if (multiscan)
            {
                scannerItem.Properties["3096"].set_Value(1);   // Сканирование по 1 странице
            }

            // Запуск сканирования с отображением статуса
            try
            {
                CommonDialogClass dlg = new CommonDialogClass();
                var scanResult = (ImageFile)dlg.ShowTransfer(scannerItem, FormatID.wiaFormatPNG, true);
                byte[] byteImage = (byte[])scanResult.FileData.get_BinaryData();
                if (multiscan)
                {
                    while (true)
                    {
                        scanResult = (ImageFile)dlg.ShowTransfer(scannerItem, FormatID.wiaFormatPNG, true);
                        byteImage = (byte[])scanResult.FileData.get_BinaryData();
                    }
                }
                scanResult.SaveFile($"file_{DateTime.Now}.png");
            }
            catch (COMException ex)
            {
                string msg = ex.Message;
                if (msg.Contains("0x80210064"))
                {
                    MessageBox.Show("Сканирование было отменено.", "Информация", MessageBoxButton.OK, MessageBoxImage.Information, MessageBoxResult.Yes);
                }
                else if (msg.Contains("0x80210003") || msg.Contains("0x80210002"))
                {
                    MessageBox.Show($"Документы отсутсвуют!", "Информация", MessageBoxButton.OK, MessageBoxImage.Information, MessageBoxResult.Yes);
                }
                else if (msg.Contains("0x80210016"))
                {
                    MessageBox.Show($"Один или несколько крышки устройства открыты!\n{ex.Message}", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);
                }
                else if (msg.Contains("0x80210006") || msg.Contains("0x8021000D") || msg.Contains("0x8021000D") || msg.Contains("0x80210005") || msg.Contains("0x80210017"))
                {
                    MessageBox.Show($"Устройство занято!", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);
                }
                else if (msg.Contains("0x8021000A") || msg.Contains("0x80210015") || msg.Contains("0x80210008") || msg.Contains("0x80210009") || msg.Contains("E_FAIL"))
                {
                    MessageBox.Show($"Сканер не подключен!", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);
                }
                else if (msg.Contains("0x8021000E") || msg.Contains("0x8021000B") || msg.Contains("0x8021000C") || msg.Contains("0x8021000F") || msg.Contains("0x80210021") || msg.Contains("0x80210020") || msg.Contains("0x80210004"))
                {
                    MessageBox.Show($"Ошибка драйвера!", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);
                }
                else
                {
                    MessageBox.Show($"Не изветсная ошибка!\n{ex.Message}", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);
                }
                return;
            }
            return;
        }

        private void GetScanners()
        {
            deviceManager = new DeviceManager();
            scanners.Clear();
            sComboBox.Items.Clear();
            foreach (DeviceInfo device in deviceManager.DeviceInfos)
            {
                if (device.Type != WiaDeviceType.ScannerDeviceType)
                {
                    continue;
                }
                scanners.Add(device);
                sComboBox.Items.Add(device.Properties["Name"].get_Value());
            }
            sComboBox.SelectedIndex = 0;
            if (scanners.Count == 0)
            {
                MessageBox.Show("Сканер не подключен!", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);
            }
        }

        private void SetParametrs()
        {
            eventIDNum.Content = parametrs[0];
        }

    }
}
