from math import exp

from kivy.core.window import Window
Window.clearcolor = (0.8,0.8,0.8,1)

from kivy.app import App
from kivy.properties import NumericProperty,StringProperty
from kivy.uix.effectwidget import EffectBase,EffectWidget

shadow_v_glsl = '''
int width = %s;
float space = %s;
float weight[%s] = %s;   //{0.16,0.15,0.12,0.09,0.05};
    
float tFrag_y = 1.0 / resolution.y;

vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{

    if (color.a != 0.0)
    {
        return color;
    }

    else
    {
    
        float sum;
    
        for (int i = 1 - width; i < width; i++)
        {
            sum += texture2D(texture, (tex_coords + vec2(0,float(i) + space) * tFrag_y)).a * weight[abs(i)];
        }

        

        return vec4(vec3(1.0),sum/2.0);
    }
}
'''

shadow_h_glsl = '''
int width = %s;
float space = %s;
float weight[%s] = %s;   //{0.16,0.15,0.12,0.09,0.05};
    
float tFrag_x = 1.0 / resolution.x;
float tFrag_y = 1.0 / resolution.y;

vec4 effect(vec4 color, sampler2D texture, vec2 tex_coords, vec2 coords)
{

    if (color.a == 1.0)
    {
        return color;
    }

    

    else
    {
    
        float sum;
        
        for (int i = 1 - width; i < width; i++)
        {
            sum += texture2D(texture, (tex_coords + vec2(float(i) - space,0) * tFrag_x)).a * weight[abs(i)];
        }

        

        return vec4(vec3(1),sum);
    }
}
'''

  
class ShadowEffect(EffectWidget):

    global shadow_v_glsl,shadow_h_glsl

    shadow_v = StringProperty(shadow_v_glsl)
    shadow_h = StringProperty(shadow_h_glsl)

    sigma = NumericProperty(3)
    shadow_width = NumericProperty(10)

    def __init__(self,**kwargs):

        super(ShadowEffect,self).__init__(**kwargs)

        weight = self.get_gaussian_weight(self.shadow_width,self.sigma)
        shadow_v_effect = EffectBase(glsl=self.shadow_v % (self.shadow_width,0,self.shadow_width,weight))#ef.format(45,45))
        shadow_h_effect = EffectBase(glsl=self.shadow_h % (self.shadow_width,0,self.shadow_width,weight))
        
        self.effects = [shadow_v_effect,shadow_h_effect]

    def gauss(self,x,s,m=0):
        '''
        mはガウス関数の釣鐘型の一番上の位置のx座標、
        s(sigma)はガウス関数の広がり具合。
        '''
        X = x - m
        gc = exp( (-1 * (X*X) / (2 * s*s)) )
        return gc

    def get_gaussian_weight(self,width,s,m=0):
        '''
        glslプログラムに埋め込むweight配列を出力する。
        #{1,2,3,4...}
        '''
        l = []
        n = 0
        for i in range(width):
            r = self.gauss(i,s)
            l.append(r)
            n += r
        return str([round(i / n,4) for i in l]).replace('[','{').replace(']','}')

    def on_sigma(self,_,sigma):

        weight = self.get_gaussian_weight(self.shadow_width,sigma) #str(list(map(lambda x: x / n,l))).replace('[','{').replace(']','}')

        shadow_v_effect = EffectBase(glsl=self.shadow_v % (self.shadow_width,0,self.shadow_width,weight))#ef.format(45,45))
        shadow_h_effect = EffectBase(glsl=self.shadow_h % (self.shadow_width,0,self.shadow_width,weight))

        self.effects = [shadow_v_effect,shadow_h_effect]

    def on_shadow_width(self,_,width):
    
        weight = self.get_gaussian_weight(width,self.sigma) #str(list(map(lambda x: x / n,l))).replace('[','{').replace(']','}')

        shadow_v_effect = EffectBase(glsl=self.shadow_v % (width,0,width,weight))#ef.format(45,45))
        shadow_h_effect = EffectBase(glsl=self.shadow_h % (width,0,width,weight))

        self.effects = [shadow_v_effect,shadow_h_effect]



if __name__ == '__main__':

    from kivy.lang import Builder

    kv = '''
BoxLayout:
    ShadowEffect:
        shadow_width: 10
        sigma: 4
        BoxLayout:
            padding: 30
            spacing: 20
            Widget:
                canvas:
                    Color:
                        rgba: 1,0,0,1
                    Rectangle:
                        pos: self.pos
                        size: self.size
            Widget:
                canvas:
                    Color:
                        rgba: 0,1,0,1
                    Rectangle:
                        pos: self.pos
                        size: self.size
            Widget:
                canvas:
                    Color:
                        rgba: 0,0,1,1
                    Rectangle:
                        pos: self.pos
                        size: self.size

        '''
    class TestApp(App):
        def build(self):
            return Builder.load_string(kv)
            
    TestApp().run()
