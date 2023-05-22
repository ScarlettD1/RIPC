using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Windows;
using Newtonsoft.Json;
using System.Net.Http;
using System.Text;
using System.Net;
using Saraff.Twain;
using System.ComponentModel;
using System.Drawing;
using System.Drawing.Imaging;
using System.Linq;
using System.Windows.Controls;
using System.Threading.Tasks;

namespace RIPC_Scanner
{
    /// <summary>
    /// Логика взаимодействия для MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private string[] parametrs = ((App)Application.Current).Parameters;
        private static readonly HttpClient client = new HttpClient();
        private Twain32 twain;

        public MainWindow()
        {
            InitializeComponent();

            // Установка переданных параметров
            SetParametrs();
            
            // Установка настроек Twain
            SetupTwain();

            // Обновление списка доступных сканеров
            GetDevices();
        }

        private void updateSButton_Click(object sender, RoutedEventArgs e)
        {
            // Обновление списка доступных сканеров
            GetDevices();
        }


        private void startScanButton_Click(object sender, RoutedEventArgs e)
        {
            // Подключение к сканеру
            try
            {
                twain.SourceIndex = sComboBox.SelectedIndex;
                if (!twain.OpenDataSource())
                {
                    MessageBox.Show("Не удалось открыть источник", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error);
                    return;
                }
            }
            catch 
            {
                MessageBox.Show("Сканер занят или недоступен.\n" +
                    "При многократной ошибке, попробуйте перезапустить компьютер и сканер.", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            // Установка необходимых параметров для сканирования
            try
            {
                twain.SetCap(TwCap.XResolution, (float)300);
                twain.SetCap(TwCap.YResolution, (float)300);
                twain.SetCap(TwCap.IPixelType, TwPixelType.RGB);
            }
            catch
            {
                MessageBox.Show($"Не возможно установить минимальные параметры для сканера.\n" +
                    $"Требования: RGB, DPI 300", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error);
                twain.CloseDataSource();
                return;
            }

            // Включение автоматического сканирования
            if (sAutoFeederCheckBox.IsChecked == true)
            {
                try
                {
                    twain.SetCap(TwCap.FeederEnabled, true);
                }
                catch
                {
                    MessageBox.Show("Не возможно использовать автоматическое сканирование страниц.", "Ошибка!",
                        MessageBoxButton.OK, MessageBoxImage.Error);
                    twain.CloseDataSource();
                    return;
                }

            }
            else
            {
                try
                {
                    twain.SetCap(TwCap.FeederEnabled, false);
                }
                catch { }
            }

            // Включение двухсторонего сканирования
            if (sDuplexCheckBox.IsChecked == true)
            {
                try
                {
                    twain.SetCap(TwCap.DuplexEnabled, true);
                }
                catch
                {
                    MessageBox.Show("Не возможно использовать двухсторонее сканирование страниц.", "Ошибка!",
                        MessageBoxButton.OK, MessageBoxImage.Error);
                    twain.CloseDataSource();
                    return;
                }
            }
            else
            {
                try
                {
                    twain.SetCap(TwCap.DuplexEnabled, false);
                }
                catch { }
            }

            // Запуск сканирования
            twain.Acquire();

            // Закрытие сессии
            twain.CloseDataSource();
            return;
        }

        private void twain_EndXfer(object sender, Twain32.EndXferEventArgs e)
        {
            // Получаем крайнее отсканированное изображение 
            var scannedImage = e.Image;

            // Переводим изображение в байты
            var byteImage = (byte[])(new ImageConverter()).ConvertTo(scannedImage, typeof(byte[]));

            // Отправляем изображение на сервис
            //SendFile(byteImage);

            // Сохраняем крайнюю страницу в файл
            string fileName = $"C:\\Ripc\\page_{twain.ImageCount}_{DateTime.Now.ToString("MMddHHmmss")}.png";
            e.Image.Save(fileName, ImageFormat.Png);
        }

        private void twain_AcquireError(object sender, Twain32.AcquireErrorEventArgs e)
        {
            Task.Run(() =>
            {
                var error = e.Exception.Message != "It worked!" ? e.Exception.Message : "";
                MessageBox.Show($"Ошибка при сканировании страниц.\n\n{error}", "Ошибка!",
                MessageBoxButton.OK, MessageBoxImage.Error);
            });
        }

        private void GetDevices()
        {
            // Очистка текущего списка сканеров
            sComboBox.Items.Clear();

            // Проход по найденым сканерам
            for (int i = 0; i < twain.SourcesCount; i++)
            {
                // Заполнение списка сканерами
                sComboBox.Items.Add(twain.GetSourceProductName(i));
            }

            // Проверка наличия сканеров
            if (sComboBox.Items.Count == 0)
            {
                MessageBox.Show("Сканер не подключен!", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);

                // Отключение кнопки сканирования
                startScanButton.IsEnabled = false;

                return;
            }

            // Включение кнопки сканирования
            startScanButton.IsEnabled = true;

            // Установка изначального сканера
            sComboBox.SelectedIndex = 0;

            return;
        }

        private void SetupTwain()
        {
            twain = new Twain32();

            // Отключение системного интерфейса
            twain.ShowUI = false;

            // Отключение Twain2.0
            twain.IsTwain2Enable = false;

            // Подписываемся на событие завершения сканирования страницы
            twain.EndXfer += twain_EndXfer;

            // Подписываемся на событие ошибки сканирования страницы
            twain.AcquireError += twain_AcquireError;


            if (!twain.OpenDSM())
            {
                MessageBox.Show("Сканер не подключен!", "Ошибка!", MessageBoxButton.OK, MessageBoxImage.Error, MessageBoxResult.Yes);

                // Отключение кнопки сканирования
                startScanButton.IsEnabled = false;
                return;
            }

        }

        private void SetParametrs()
        {
            // Установка ID мероприятия на старинце
            eventIDNum.Content = parametrs[0];
        }

        private async void SendFile(byte[] file)
        {
            var data = new
            {
                event_id = parametrs[0],
                organization_id = parametrs[1],
                byte_file = file
            };

            // Сериализуем данные в JSON строку
            var json = JsonConvert.SerializeObject(data);

            // Создаем HTTP клиент и отправляем POST запрос
            var content = new StringContent(json, Encoding.UTF8, "application/json");
            var response = await client.PostAsync("", content);

            // Проверяем ответ
            if (!response.IsSuccessStatusCode)
            {
                throw new Exception(response.StatusCode.ToString());
            }
            return;
        }

        protected override void OnClosing(CancelEventArgs e)
        {
            // Закрытие сессии twain
            twain.CloseDSM();

            base.OnClosing(e);
            return;
        }

    }
}
